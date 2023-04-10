from flask import Flask, request
import greeting_pb2
import greeting_pb2_grpc
import grpc
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator



app = Flask(__name__)

resource = Resource(attributes={
    "service.name": "python-demo"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)




@app.route('/greeting')
def greeting():
    with tracer.start_as_current_span("http") as http_span:
        name = request.args.get('name', 'World')
        message = request.args.get('message', 'Hello')
        http_span.set_attribute("http_span_attribute", "http_span_attribute_value")
        with tracer.start_as_current_span("grpc-client") as grpc_span:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = greeting_pb2_grpc.GreeterStub(channel)
                response = stub.greet(greeting_pb2.ClientInput(name=name, greeting=message))
    return response.message

if __name__ == '__main__':
    app.run()
