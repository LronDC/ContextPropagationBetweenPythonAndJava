# Explanation

TBD

# How to use
- Setup Java server:

    Under the `javasnippet` directory and execute:
    `mvn compile && mvn clean install`
    `mvn exec:java -Dexec.mainClass="com.demo.App" -e`
    output:
    ```console
    [INFO] Scanning for projects...
    [INFO]
    [INFO] ------------------------< com.demo:javasnippet >------------------------
    [INFO] Building javasnippet 1.0-SNAPSHOT
    [INFO] --------------------------------[ jar ]---------------------------------
    [INFO]
    [INFO] --- maven-resources-plugin:3.0.2:resources (default-resources) @ javasnippet ---
    [INFO] Using 'UTF-8' encoding to copy filtered resources.
    [INFO] skip non existing resourceDirectory /Users/ron/ContextPropagationBetweenPythonAndJava/http/javasnippet/src/main/resources
    [INFO]
    [INFO] --- maven-compiler-plugin:3.8.0:compile (default-compile) @ javasnippet ---
    [INFO] Nothing to compile - all classes are up to date
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD SUCCESS
    [INFO] ------------------------------------------------------------------------
    [INFO] Total time:  1.684 s
    [INFO] Finished at: 2023-04-10T18:10:04+08:00
    [INFO] ------------------------------------------------------------------------
    [INFO] Error stacktraces are turned on.
    [INFO] Scanning for projects...
    [INFO]
    [INFO] ------------------------< com.demo:javasnippet >------------------------
    [INFO] Building javasnippet 1.0-SNAPSHOT
    [INFO] --------------------------------[ jar ]---------------------------------
    [INFO]
    [INFO] --- exec-maven-plugin:3.1.0:java (default-cli) @ javasnippet ---
    Server started at: Mon Apr 10 18:10:08 CST 2023
    ```
- Setup Python server:

    Under the `pythonsnippet` directory and execute:
    `python server.py`
    output:
    ```console
    * Serving Flask app 'server'
    * Debug mode: off
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    ```
- Make call to Python server:

`curl http://127.0.0.1:5000/python`
- Checkout Jaeger UI:

    example:
    
    <img width="756" alt="截屏2023-04-10 18 25 27" src="https://user-images.githubusercontent.com/59912384/230885156-11a7289d-4054-4da5-be21-ab33bef4f141.png">
    
    <img width="1509" alt="截屏2023-04-10 18 25 49" src="https://user-images.githubusercontent.com/59912384/230885280-35b31829-e048-48fa-acd7-88a697624ac3.png">

    <img width="1508" alt="截屏2023-04-10 18 26 24" src="https://user-images.githubusercontent.com/59912384/230885304-0de11bf1-e537-4182-9151-fb715790588a.png">


   
    
