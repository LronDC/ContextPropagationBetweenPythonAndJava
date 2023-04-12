package com.demo;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URL;
import java.net.HttpURLConnection;
import java.util.Date;
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.baggage.Baggage;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.api.baggage.propagation.W3CBaggagePropagator;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.context.propagation.TextMapGetter;
import io.opentelemetry.context.propagation.TextMapPropagator;
import io.opentelemetry.context.propagation.TextMapSetter;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes;
import io.opentelemetry.semconv.trace.attributes.SemanticAttributes;

public class App {
    static class MyHandler implements HttpHandler {
        // Create a resource
        Resource resource = Resource.getDefault()
            .merge(Resource.create(Attributes.of(ResourceAttributes.SERVICE_NAME, "java-service")));
      
        // Create a span exporter
        OtlpGrpcSpanExporter spanExporter = OtlpGrpcSpanExporter.builder().setEndpoint("http://jaeger:4317").build();

        // Create a tracer provider
        SdkTracerProvider sdkTracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
            .setResource(resource)
            .build();

        // Create an OpenTelemetry SDK
        OpenTelemetry openTelemetry = OpenTelemetrySdk.builder()
            .setTracerProvider(sdkTracerProvider)
            .setPropagators(ContextPropagators.create(TextMapPropagator.composite(W3CTraceContextPropagator.getInstance(), W3CBaggagePropagator.getInstance())))
            .buildAndRegisterGlobal();
      
        // Create a tracer
        Tracer tracer = openTelemetry.getTracer("java-snippet", "0.1.0");

        // Define a TextMapGetter to extract context from HttpExchange
        TextMapGetter<HttpExchange> getter = new TextMapGetter<HttpExchange>() {
            @Override
            public String get(HttpExchange carrier, String key) {
            if (carrier.getRequestHeaders().containsKey(key)) {
                return carrier.getRequestHeaders().get(key).get(0);
            }
            return null;
            }

            @Override
            public Iterable<String> keys(HttpExchange carrier) {
                return carrier.getRequestHeaders().keySet();
            }
        };

        // Define a TextMapSetter to inject context into HttpURLConnection
        TextMapSetter<HttpURLConnection> setter = new TextMapSetter<HttpURLConnection>() {
            @Override
            public void set(HttpURLConnection carrier, String key, String value) {
            // Insert the context as Header
            carrier.setRequestProperty(key, value);
            }
        };


        @Override
        public void handle(HttpExchange t) throws IOException {
            // Extract context from HttpExchange
            Context extractedContext = openTelemetry.getPropagators().getTextMapPropagator()
                .extract(Context.current(), t, getter);
            System.out.println("Extracted context: " + extractedContext);
            
            try (Scope scope = extractedContext.makeCurrent()) {
                // Automatically use the extracted SpanContext as parent.
                Span inComeSpan = tracer.spanBuilder("java-incomming-span")
                    .setSpanKind(SpanKind.SERVER)
                    .startSpan();
                try {
                    // Add the attributes defined in the Semantic Conventions
                    // Read the baggage from the current Context propagated from the Python service
                    String baggage = Baggage.current().getEntryValue("python-baggage-key");
                    System.out.println("Baggage: " + baggage);
                    inComeSpan.setAttribute("python-baggage-key", baggage);
                    inComeSpan.setAttribute(SemanticAttributes.HTTP_METHOD, t.getRequestMethod());
                    inComeSpan.setAttribute(SemanticAttributes.HTTP_CLIENT_IP, t.getRemoteAddress().getAddress().getHostAddress());
                    inComeSpan.setAttribute(SemanticAttributes.HTTP_TARGET, t.getRequestURI().toString());
                    // Create an Out-going child Span
                    Span outGoSpan = tracer.spanBuilder("java-outgoing-span")
                        .setParent(Context.current().with(inComeSpan))
                        .setSpanKind(SpanKind.CLIENT).startSpan();
                    try {
                        // Keep the baggage from the Python service
                        outGoSpan.setAttribute("python-baggage-key", baggage);
                        // Add new Java baggage to the current Context
                        Baggage.current().toBuilder().put("java-baggage-key", "java-baggage-value").build().makeCurrent();
                        // Create a new HttpURLConnection to send a request to the Python service
                        URL url = new URL("http://pythonsnippet:8001/python/server");
                        HttpURLConnection transportLayer = (HttpURLConnection) url.openConnection();
                        // Inject the request with the *current*  Context, which contains our current Span.
                        openTelemetry.getPropagators().getTextMapPropagator().inject(Context.current(), transportLayer, setter);
                        // Send the request and receive the response
                        transportLayer.connect();
                        InputStream responseStream = transportLayer.getInputStream();
                        BufferedReader responseReader = new BufferedReader(new InputStreamReader(responseStream));
                        StringBuilder responseBuilder = new StringBuilder();
                        String line;
                        while ((line = responseReader.readLine()) != null) {
                            responseBuilder.append(line);
                        }
                        String response = responseBuilder.toString();
                        // Set the response headers
                        Headers headers = t.getResponseHeaders();
                        headers.set("Content-Type", "text/plain");
                        // Set the response body
                        byte[] responseBytes = response.getBytes();
                        t.sendResponseHeaders(200, responseBytes.length);
                        OutputStream os = t.getResponseBody();
                        // Send the response to python service
                        os.write(responseBytes);
                        os.close();
                    } finally {
                        outGoSpan.end();
                    }
                } finally {
                    inComeSpan.end();
                }
            }
        }
    }


    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
        server.createContext("/java", new MyHandler());
        server.setExecutor(null); // creates a default executor
        server.start();
        System.out.println("Server started at: " + new Date());
    }
}


