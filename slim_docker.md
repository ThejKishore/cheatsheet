Creating a minimal Docker image for a Spring Boot application using JRE 21 and optimizing the image size with `jlink` involves several steps. Below is an example Dockerfile that accomplishes this.

### Step 1: Prepare Your Spring Boot Application

Ensure your Spring Boot application is built with all the necessary dependencies. You can use Maven or Gradle to build your application and package it as a JAR.

### Step 2: Use `jlink` to Create a Custom Runtime Image

1. **Create a Custom JRE with `jlink`**:
   You can create a custom runtime image that includes only the modules you need. Here’s how you can do it using a command line:

   ```bash
   jlink --module-path $JAVA_HOME/jmods:target/myapp.jar \
         --add-modules your.main.module \
         --output custom-jre \
         --name myapp-runtime
   ```

   Replace `your.main.module` with the actual module name of your Spring Boot application. This command generates a minimal runtime image in the `custom-jre` directory.

### Step 3: Create a Dockerfile

Here's a minimal Dockerfile to create a Docker image for your Spring Boot application:

```dockerfile
# Use a minimal base image with JRE 21
FROM eclipse-temurin:21-jre

# Set working directory
WORKDIR /app

# Copy the custom JRE
COPY custom-jre /app/custom-jre

# Copy your application JAR, libs, classes, and resources
COPY target/myapp.jar /app/myapp.jar

# Set the JAVA_HOME environment variable
ENV JAVA_HOME=/app/custom-jre
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Command to run the application
CMD ["java", "-jar", "/app/myapp.jar"]
```

### Step 4: Build the Docker Image

1. Build your Spring Boot application:
   ```bash
   ./mvnw clean package
   ```

2. Create a custom JRE using `jlink` as shown earlier.

3. Build the Docker image:
   ```bash
   docker build -t my-spring-boot-app .
   ```

### Step 5: Run Your Docker Container

Run your container using the following command:

```bash
docker run -d --name my-spring-boot-app-container my-spring-boot-app
```

### Notes

- **Base Image**: The base image used here is `eclipse-temurin:21-jre`, which is a lightweight OpenJDK 21 runtime.
- **`jlink`**: By using `jlink`, you can create a custom JRE that contains only the necessary modules, significantly reducing the image size.
- **Directory Structure**: Ensure the structure of your `custom-jre` directory matches what you have in the Dockerfile.
- **Application JAR**: The `myapp.jar` file should contain all necessary resources and dependencies.

### References

- [Docker Documentation](https://docs.docker.com/)
- [Java JLink Documentation](https://openjdk.java.net/jeps/392)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)

This setup will give you a lightweight Docker image for your Spring Boot application, utilizing JRE 21 and optimized with `jlink`.
