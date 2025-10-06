import org.yaml.snakeyaml.Yaml
import java.io.FileWriter

// Use buildscript block to apply dependency
buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath("org.yaml:snakeyaml:2.2") // Add your preferred YAML library
    }
}

// Define the task
tasks.register("generateValuesYaml") {
    group = "custom"
    description = "Generates a values.yaml file using SnakeYAML"

    doLast {
        val data = mapOf(
            "app" to mapOf(
                "name" to "my-app",
                "version" to "1.0.0"
            ),
            "replicaCount" to 3,
            "image" to mapOf(
                "repository" to "my-docker-repo/my-app",
                "tag" to "latest"
            )
        )

        val yaml = Yaml()
        val file = file("$buildDir/generated/values.yaml")
        file.parentFile.mkdirs()
        file.writer().use {
            yaml.dump(data, it)
        }

        println("Generated: ${file.absolutePath}")
    }
}
