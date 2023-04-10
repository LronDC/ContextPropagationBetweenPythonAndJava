from flask import Flask, jsonify
import requests
import flask
# Import the necessary OpenTelemetry packages
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry import propagate, baggage

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


"""
This is the entrance function that should be called when the Python server is started.
"""
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

"""
This is the call-back function that will be called when the Java server is called by Python client up above.
"""
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
    

if __name__ == '__main__':
    app.run()