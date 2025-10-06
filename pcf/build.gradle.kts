apply(from = "gradle/generate-values.gradle.kts")

// Optionally, you can hook it into build lifecycle
tasks.named("build") {
    dependsOn("generateValuesYaml")
}
