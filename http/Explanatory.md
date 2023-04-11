# Overview

The **http** section setup two http services, one in Python and one in Java, to simulate the context propagation between e.g. micorservices.

It takes python service as entry point, and then calls java service, propagates the trace context as well as some baggage data, then java service calls back at python service on another endpoint, continue to propagate the trace context and baggage data downward. At last, there will be only one trace that starts from python service which contains four spans, two of them are from python service, and the other two are from java service.

It uses Jaeger as the trace collector.

![logic](https://user-images.githubusercontent.com/59912384/231078152-914ec322-7be0-4a64-9e9b-9fe82b683ed0.png)

# Python

Let's take a look at Python code.

- **set up for opentelemtry**

```python
# Create a Resource object with a service name attribute
resource = Resource.create({"service.name": "python-service"})

# Create a TracerProvider with the OTLPSpanExporter and the Resource object
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Set the tracer to the global tracer
tracer = trace.get_tracer(__name__)
# Set the global propagator to extract context
PROPAGATOR = propagate.get_global_textmap()

app = Flask(__name__)
```

- **inject trace context and baggage for out-going request**

```python
@app.route('/python')
def client():
    # Start a span named python-client-span
    with tracer.start_as_current_span("python-client-span") as python_span:
        # Set attributes defined in the semantic conventions
        python_span.set_attribute("http.method", flask.request.method)
        python_span.set_attribute("http.url", flask.request.url)
        # Set Python baggage and get the new context
        ctx = baggage.set_baggage("python-baggage-key", "python-baggage-value")
        # Inject the context into the carrier
        carrier = {}
        TraceContextTextMapPropagator().inject(carrier=carrier, context=ctx)
        W3CBaggagePropagator().inject(carrier=carrier, context=ctx)
        # Debugging context and carrier values
        print(ctx)
        print(carrier)
        # MUST add the values to the header
        header = {"traceparent": carrier["traceparent"], "baggage": carrier["baggage"]}
        # Make a GET request to the Java server
        java_response = requests.get('http://localhost:8000/java', headers=header)
        # get the response content from the Java server
        java_response_content = java_response.content
    # return the response content as a JSON object
    return jsonify({'response': java_response_content.decode('utf-8')})
```
This's the entry function. First start a span named `python-client-span`, set some attributes, set baggage data, `baggage.set_baggage()` returns a `Context` object. A [Carrier](https://opentelemetry.io/docs/reference/specification/context/api-propagators/#carrier) object is needed to carry the context so we can propagate it, we intend to propagate both trace context and baggage to downstream service, thus we need two types of propagators`TraceContextTextMapPropagator`and `W3CBaggagePropagator`. After call `inject()` the `carrier` will generate some key-value data, e.g. `{'traceparent': '00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01', 'baggage': 'python-baggage-key=python-baggage-value'}`. **Remember** to add the values to the header, then we can make a request to the Java server, the Trace Context and Baggage data will be propagated to.

- **extract trace context and baggage from in-comming request**

```python
@app.route('/python/server')
def server():
    # Extract context from incoming request
    ctx = PROPAGATOR.extract(flask.request.headers)
    # Start a span named python-server-span from the context
    with tracer.start_as_current_span("python-server-span", context=ctx) as python_span:
        # Get the baggage from the context propagated from the Java server
        java_baggage = baggage.get_baggage("java-baggage-key", context=ctx)
        python_baggage = baggage.get_baggage("python-baggage-key", context=ctx)
        python_span.set_attribute("java-baggage-key", java_baggage)
        python_span.set_attribute("python-baggage-key", python_baggage)
    return jsonify({'response': 'Hello from Python!'})
```
This function is for the Java server to call back, it shows how Python extracts the context from an incoming request. We get a default propagator by `propagate.get_global_textmap()`, it returns composite propagator that contains both `TraceContextTextMapPropagator` and `W3CBaggagePropagator`, then we can call `extract()` to extract the context and baggage from the header from upstream service. 

# Java

- **set up for opentelemtry**

```java
// Create a resource
Resource resource = Resource.getDefault()
    .merge(Resource.create(Attributes.of(ResourceAttributes.SERVICE_NAME, "java-service")));

// Create a span exporter
OtlpGrpcSpanExporter spanExporter = OtlpGrpcSpanExporter.builder().setEndpoint("http://localhost:4317").build();

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
```
Notice `.setPropagators(ContextPropagators.create(TextMapPropagator.composite(W3CTraceContextPropagator.getInstance(), W3CBaggagePropagator.getInstance())))`, we intend to propagate both trace context and baggage to downstream service, thus we need multi propagators`W3CTraceContextPropagator`and `W3CBaggagePropagator`. `TextMapPropagator.composite()` can combine multiple propagators into one.

- **extrace trace context and baggage from in-comming request**

Fisrt we need to define a `TextMapGetter` to extract the context from the header.

```java
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
```
then get extracted context, make it current.
```java
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
```
There we can add new span in current context and get baggage data and other operations you want.

- **continue to propagate trace context and baggage to downstream service**

```java
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
    URL url = new URL("http://localhost:5000/python/server");
    HttpURLConnection transportLayer = (HttpURLConnection) url.openConnection();
    // Inject the request with the *current*  Context, which contains our current Span.
    openTelemetry.getPropagators().getTextMapPropagator().inject(Context.current(), transportLayer, setter);
```
We use `inject()` to inject request with current context to header.

- **servce the request**

```java
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
```
Don't forget to close the span.

# Let‘s look at the effect

When you make the call to `http://127.0.0.1:5000/python`, you will see the **one** trace in the Jaeger UI.

<img width="1511" alt="截屏2023-04-11 14 20 50" src="https://user-images.githubusercontent.com/59912384/231077904-6629caf0-4a99-4afb-af43-45557ecea589.png">

This means the trace context created in Python service is propagated to Java service, and be propagated back to Python service. There what should have been two traces became one. Whether `python-service` or `java-service` trace is the same one.

Take a closer look at the details.

<img width="1510" alt="截屏2023-04-11 14 30 55" src="https://user-images.githubusercontent.com/59912384/231077958-3a5699b0-f1ab-46eb-b8f5-4d8360285c42.png">

Java service catch the baggage filled in Python service: `python-baggage-key=python-baggage-value`.

A child span was created with `java-incomming-span` as parent, and the baggage was added as attribute.

<img width="1512" alt="截屏2023-04-11 14 35 05" src="https://user-images.githubusercontent.com/59912384/231078009-94bfd7e2-8d02-441c-bf82-417ef960e6ff.png">

Finally, context and baggage are propagated to Python service, a span was created in Python service and it had same span level with the span `java-incomming-span`(the parent).

<img width="1511" alt="截屏2023-04-11 14 38 25" src="https://user-images.githubusercontent.com/59912384/231078047-6880487b-030a-4116-a4ef-1c7cc95bf9bb.png">
