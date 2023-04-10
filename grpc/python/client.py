import grpc

import greeting_pb2
import greeting_pb2_grpc
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.instrumentation.grpc._client import OpenTelemetryClientInterceptor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
resource = Resource(attributes={
    "service.name": "python-test-client"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

grpc_client_instrumentor = GrpcInstrumentorClient()
grpc_client_instrumentor.instrument()

def run():
   with tracer.start_as_current_span("grpc-client") as grpc_span:
      grpc_span.set_attribute("grpc_span_client_attribute", "grpc_span_attribute_client_value")
      with grpc.insecure_channel('localhost:50051') as channel:
         stub = greeting_pb2_grpc.GreeterStub(channel)
         response = stub.greet(greeting_pb2.ClientInput(name='John', greeting = "Yo"))
      print("Greeter client received following from server: " + response.message)   
run()
