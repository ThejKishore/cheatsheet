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

import com.bmuschko.gradle.docker.tasks.image.DockerBuildImage 
import com.bmuschko.gradle.docker.tasks.image.Dockerfile

buildscript{
    repositories{
        mavenLocal()
        mavenCentral()
    }
    dependecies{
        classpath "com.bmuschko:gradle-docker-plugin:4.8.1"
    }
}

task createDockerfile(type: Dockerfile) { 
    destFile = project.file("build/docker/") 
    from "openjdk8:alphine" maintainer "Thej kishore 'kishores1984@gmail.com'" 
    copyFile "libs/${jar.baseName}-${jar.version}.jar", "${jar.baseName}-${jar.version}.jar" 
    copyFile "resources/*" , "resources/" 
    user 'jcpsvcon' 
    entryPoint '/java.sh', '-jar', "${jar.baseName}-${jar.version}.jar", "--spring.application.name=authentication-service-v1" ,"--spring.config.additional-location=file:application.yml" 
}

task buildDockerImage(type: DockerBuildImage) { 
    dependsOn assemble, createDockerfile 
    inputDir = createDockerfile.destFile.parentFile 
    pull = false
    tag = "something:latest" 
}
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

