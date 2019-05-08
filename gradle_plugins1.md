import com.bmuschko.gradle.docker.tasks.image.DockerBuildImage
import com.bmuschko.gradle.docker.tasks.image.Dockerfile

task createLocalDockerfile(type: Dockerfile) {
    destFile = project.file("build/docker/")
    from "openjdk8:alphine"
    maintainer "Thej kishore 'kishores1984@gmail.com'"
    copyFile "libs/${jar.baseName}-${jar.version}.jar", "${jar.baseName}-${jar.version}.jar"
    copyFile "resources/*" , "resources/"
    user 'jcpsvcon'
    entryPoint '/java.sh', '-jar', "${jar.baseName}-${jar.version}.jar",  "--spring.application.name=authentication-service-v1"  ,"--spring.config.additional-location=file:application.yml"
    versionLabels()
}

task buildDockerImage(type: DockerBuildImage) {
    dependsOn assemble, createDockerfile
    inputDir = createDockerfile.destFile.parentFile
    pull = false
    tag = "${registryName}/auth-rs:${project.versionInfo.dockerTag}"
}
