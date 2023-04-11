# Context Propagation Between Python And Java
> This project is a learning example for context propagation between Python and Java.

## introduction
This Project demonstrates the [Context Propagation](https://opentelemetry.io/docs/concepts/signals/traces/#context-propagation) capability of OpenTelemetry (OTel) between Python and Java service. Project is divided into two parts: **gRPC** and **HTTP** -- designed to show the differ between two protocols. Each part contains subdirectories which contain the Java/Python code respectively. The **grpc** directory also contains the .proto file. Further infomation please look into [grpc's](https://github.com/LronDC/ContextPropagationBetweenPythonAndJava/tree/main/grpc) or [http's](https://github.com/LronDC/ContextPropagationBetweenPythonAndJava/tree/main/http) README.md file and the Explanatory.md.
## code structure
```shell
.
├── README.md
├── grpc
└── http
```
- **grpc**: Both Python and Java use **gRPC** to implement OTel context propagation. It's [WIP] and any contribution or help is welcome.
- **http**: Both Python and Java use **HTTP** to implement OTel context propagation. [how to use](https://github.com/LronDC/ContextPropagationBetweenPythonAndJava/blob/main/http/README.md)
### grpc
*TBD*
### http
```shell
.
├── javasnippet
└── pythonsnippet
```
- **javasnippet**: Java code snippet for context propagation. It's maven project.
- **pythonsnippet**: Python code snippet for context propagation. It's flask project.

## Reference documents

https://github.com/laziobird/opentelemetry-jaeger/blob/main/docs/%E9%93%BE%E8%B7%AF%E6%95%B0%E6%8D%AE%E5%A6%82%E4%BD%95%E4%BC%A0%E6%92%AD%20.md

https://opentelemetry-python.readthedocs.io/

https://opentelemetry-python-contrib.readthedocs.io/

https://opentelemetry.io/docs/instrumentation/java/manual

https://opentelemetry.io/docs/instrumentation/python/manual/
