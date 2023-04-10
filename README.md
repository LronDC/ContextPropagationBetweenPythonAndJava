# Context Propagation Between Python And Java
> This project is a learning example for context propagation between Python and Java.

## introduction
Project is divided into two parts: **gRPC** and **HTTP**. Each part contains two subdirectories: **java** and **python**. The **java** directory contains the Java code, and the **python** directory contains the Python code. The **grpc** directory also contains the .proto file.
## code structure
```shell
.
├── README.md
├── grpc
└── http
```
- **grpc**: Both Python and Java use **gRPC** to implement OTel context propagation. It's [WIP] and any contribution or help is welcome.
- **http**: Both Python and Java use **HTTP** to implement OTel context propagation. [how to use]
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
