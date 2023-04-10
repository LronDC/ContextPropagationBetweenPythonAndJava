from concurrent import futures

import grpc
import greeting_pb2
import greeting_pb2_grpc
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator



resource = Resource(attributes={
    "service.name": "python-demo"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)


class Greeter(greeting_pb2_grpc.GreeterServicer):
   def greet(self, request, context):
      trace_ctx = TraceContextTextMapPropagator().extract(carrier=request)
      print(trace_ctx)
      with tracer.start_as_current_span("grpc-server"):
         print("Starting gRPC server")
      print("Got request " + str(request))
      return greeting_pb2.ServerOutput(message='{0} {1}!'.format(request.greeting, request.name))
	  
def server():
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
   greeting_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
   server.add_insecure_port('[::]:50051')
   print("gRPC starting")
   server.start()
   server.wait_for_termination()
server()
