# Context Propagation Between Python And Java
> This project is a learning example for context propagation between Python and Java.

## introduction
Project is divided into two parts: **gRPC** and **HTTP**. Each part contains two subdirectories: **java** and **python** contains the Java/Python code respectively. The **grpc** directory also contains the .proto file. Further infomation please look into [grpc's](https://github.com/LronDC/ContextPropagationBetweenPythonAndJava/tree/main/grpc) or [http's](https://github.com/LronDC/ContextPropagationBetweenPythonAndJava/tree/main/http) README.md file.
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
