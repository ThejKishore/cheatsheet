## Gradle





### if a task depends on other task

compile.dependOn(copyTas)

### if a task needs to be executed after a certain task

build.finalizeBy(deleteTask)

### helper tasks

#### copy dependency libraries

```groovy
task copyLibs(type: Copy){
    into "${buildDir}/lib"
    from configurations.compile
}

```

#### unzip jars

```groovy
task unZipJar(type:Copy){
    from zipTree("${buildDir}/lib/something.jar")
    into "${buildDir}/temp"
}

```


#### rename task jars

```groovy
task rename(type: Copy){
    into "${buildDir}/lib/"
    from "${buildDir}/lib/something.jar"
    rename "something.jar" "something1.jar"
}

```


### writinga custom jar

task customJar(type: Jar){
    into("META-INF/something"){
        include('**/*.sjon')
        from("src/main/resource/json")
    }
    classifier = "stubs"
}


### maven plugin

```groovy

apply plugin: 'maven'

repositories{
    maven{
        credentials{
            username "${maven_user_name}"
            password "${maven_user_credentials}"
        }
        url "file://${user_home}/.m2/repositories"
    }

    uploadArchives{
        repositories{
            mavenDeployer {
                repository{
                    url: "file://${user_home}/.m2/repositories"
                    authentication(userName: maven_user_name, password: maven_user_credentials)
                }
            }
        }
    }
}
```



### bmuschko Docker plugin 

```groovy
plugins {
    id 'org.springframework.boot' version '2.1.5.RELEASE'
    id 'java'
    id 'com.bmuschko.docker-remote-api' version '3.5.0'
}

import com.bmuschko.gradle.docker.tasks.image.Dockerfile
import com.bmuschko.gradle.docker.tasks.image.DockerBuildImage

apply plugin: 'io.spring.dependency-management'

group = 'com.kish.learning'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '1.8'

configurations {
    developmentOnly
    runtimeClasspath {
        extendsFrom developmentOnly
    }
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
    jcenter()
}

ext {
    set('springCloudVersion', "Greenwich.SR1")
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
    compileOnly 'org.projectlombok:lombok'
    developmentOnly 'org.springframework.boot:spring-boot-devtools'
    annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
    }
}

/*
docker {
    registryCredentials {
        username = getConfigurationProperty('DOCKER_USERNAME', 'docker.username')
        password = getConfigurationProperty('DOCKER_PASSWORD', 'docker.password')
        email = getConfigurationProperty('DOCKER_EMAIL', 'docker.email')
    }
}

String getConfigurationProperty(String envVar, String sysProp) {
    System.getenv(envVar) ?: project.findProperty(sysProp)
}
*/

/**
 * needed in mac to work
 */
task dockerCopy(type: Copy){
    into "${buildDir}/docker/libs"
    from "${buildDir}/libs"
}

task createDockerfile(type: Dockerfile) {
    def path = project.buildDir
    println "$path"
    destFile = project.file('build/docker/Dockerfile')
    from 'openjdk:8-jre-alpine'
    maintainer 'Thej Kishore "kishores1984@gmail.com"'
    workingDir("/app")
    copyFile "libs/${jar.baseName}-${jar.version}.jar" , "/app/${jar.baseName}-${jar.version}.jar"
    entryPoint "java"
    defaultCommand "-jar", "/app/${jar.baseName}-${jar.version}.jar"
    exposePort 8080
    runCommand 'apk --update --no-cache add curl'
    instruction 'HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1'
}

task buildImage(type: DockerBuildImage) {
    dependsOn createDockerfile
    inputDir = createDockerfile.destFile.parentFile
    tag = "thej/discoverclientdemo:$jar.version"
}

createDockerfile.dependsOn assemble,dockerCopy


```

### download plugin 

```groovy

buildscript{
    repositories{
        mavenCentral()
    }

    dependencies{
        classpath 'de.undercouch:gradle-download-task:3.4.3'
    }
}

apply plugin: 'de.undercouch.download'


task download(type:Download) {
    src "https://maven.net/repositroy/org/springframework/something.jar"
    dest new File(buildDir,"temp/something.jar")
}

```

### Git Plugin Ggrit

```groovy

buildscript{
    repositories{
        mavenCentral()
    }

    dependencies{
        classpath 'org.ajobertar:grgit:2.3.0'
        classpath 'org.ajobertar:gradle-grgit:1.7.2'
    }
}


//System.propertie
//org.ajobster.grgit.auth.username=
//org.ajobster.grgit.auth.password=
//.bash_profile
// export GRGIT_USER=
// export GRGIT_PASSWORD=

task cloneRepo(){
    def file=new File("${buildDir}/temp-git)
    if(file.exits() && file.isDirectory()){
        file.deleteDir()
    }
    def git = Grgit.clone(dir: "${buildDir}/temp-git" , uri:"https://github.com/thejkishore/cheatsheet.git")
}
```

#### writing the gradle plugin 


build.gradle

```groovy

plugins{
    id 'java-gradle-plugin'
    id 'groovy'

}

dependencies{

}

gradlePlugin {
    plugins {
        yourPluginName{
            id = "com.kish.something"
            implementationClass = "com.kish.learning.Plugin"
        }
    }
}

```

