#### Docker File Sample

Docker file sample . The file name should be Docker
```jshelllanguage
FROM redis:alpine
COPY redis.conf /usr/local/etc/redis/redis.conf
RUN mkdir /redis
CMD ["redis-server","/usr/local/etc/redis/redis.conf"]

```

#### Creating docker image:

```script
docker build . -t ${label_name}
```

#### Running the docker image
```jshelllanguage
docker run -d --cap-add sys_resource --name ${service_name} -p ${from_port}:${to_port} -t ${image_name}
```

#### Docker cmds
```jshelllanguage
#Stopping the service using the image name
docker stop ${image_name}

#killing the service using the image name
docker kill ${image_name}

# remove the image from the repository
docker rmi ${image_name}

# lists all docker images with state
docker ps -a

#execute the comd in the container
docker exec -it ${image_name|service_name} ${cmd}
docker exec -it redis_enterprise bash
```


#### Docker machine

```dockerfile

docker-machine create --driver=virtualbox myhost


docker-machine --version


docker-machine ip

docker-machine env myhost

# run this cmd to configure the shell
eval $(docker-machine env myhost)

docker image ls


docker image rm-f $(docker image ls -aq)
docker container rm-f $(docker containe ls -aq)

```

# Running Docker

```docker
docker --version
---
docker info
---
docker version
---
docker --help
---
docker image ls
---
docker container ls
---
docker node ls
---
docker container run ${image}

##running in interactive mode and tty mode
docker container run -it ${image}
docker container run -d ${image}

docker container stop ${containername}

docker container ls -a

docker container rm ${containername}

--assigning a name

docker container run -d --name ${containername}  ${image}


docker container rm -f ${conatinername}

docker container run  --name  ${containername} ${imagename} bash

//expose port in predefined range
docker container run -d --name ${cn} -P ${imgn}


docker container run -d --name ${cn} -p 8080:8080 ${imgn}


docker container run -d --name ${cn} -p 8080:8080 -v `pwd` /wepp.war:/opt/jboss/wildfly  ${imgn}





```


#### Docker file instruction

Docker file hello world

##### FROM and CMD
```
FROM ubuntu

CMD echo "hello World"

```

Docker file for java
public registry  https://hub.docker.com
```
FROM openjdk
CMD java -version

```

```
FROM opendjdk:jdk-alpine
CMD java -version
```

##### COPY

```
FROM openjdk:jdk-alpine
COPY ${jar}  ${deploymentpath}
CMD java -jar ${deployementpath}/${jar}
```

##### EXPOSE

### DOCKER image
```
docker image  --help

-t tag name
docker image build -t ${tagname} .



```

### MAVEN DOCKER plugin

group : io.fabric8
artifact:maven-docker-plugin

#### gradle

grp : com.bmuschko
atrid: docker-java-plugin


### docker-compose
file must be docker-compose.yml

```yaml

version: '3'
services:
  web:
    image: arungupta/couchbase-javaee:travel
    environment:
      - COUCHBASE_URI=db
    ports:
      - 8080:8080
      - 9990:9990
    depends_on:
      - db
  db:
    image: arungupta/couchbase:travel
    ports:
      - 8091:8091
      - 8092:8092
      - 8093:8093
      - 11210:11210


```


#### Docker-Swarm

```
# enabling swarm in docker


    ensure odd no of swarm managers

    worker node


 docker swarm --help

 docker swarm init

 docker info


docker swarm join --token <manger_toke> --listen-addr <master2> <master1>


```