FROM maven:latest

COPY . /usr/src/myapp

WORKDIR /usr/src/myapp

RUN mvn compile && mvn clean install

EXPOSE 8000/tcp

CMD ["mvn", "exec:java", "-Dexec.mainClass=com.demo.App", "-e"]