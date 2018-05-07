### Open Source Project to know

##### 1. [Dagger2](https://google.github.io/dagger/) (Dependency Injection)
[User-Guide](https://google.github.io/dagger/users-guide)

```groovy

// Add plugin https://plugins.gradle.org/plugin/net.ltgt.apt

plugins {
  id "net.ltgt.apt" version "0.10"
}

// Add Dagger dependencies

dependencies {
  compile 'com.google.dagger:dagger:2.x'
  apt 'com.google.dagger:dagger-compiler:2.x'
}

```



##### 2. [OKHttp](http://square.github.io/okhttp/)
```gradle
compile 'com.squareup.okhttp3:okhttp:3.10.0'

```

```xml
<dependency>
  <groupId>com.squareup.okhttp3</groupId>
  <artifactId>okhttp</artifactId>
  <version>3.10.0</version>
</dependency>
```

[user_guide](http://www.baeldung.com/guide-to-okhttp)

##### 3. [Retrofit](http://square.github.io/retrofit/)

```groovy
compile 'com.squareup.retrofit2:retrofit:2.4.0'
```

```xml
<dependency>
  <groupId>com.squareup.retrofit2</groupId>
  <artifactId>retrofit</artifactId>
  <version>2.4.0</version>
</dependency>
```
[user_guide](http://www.vogella.com/tutorials/Retrofit/article.html)


##### 4. [JDeffered](http://jdeferred.org/)


```groovy
compile 'org.jdeferred.v2:jdeferred-core:${version}'
```

```xml
<dependency>
    <groupId>org.jdeferred.v2</groupId>
    <artifactId>jdeferred-core</artifactId>
    <version>${version}</version>
</dependency>
```

##### 5. [MBassador](https://github.com/bennidi/mbassador/wiki)

```groovy
// https://mvnrepository.com/artifact/net.engio/mbassador
compile group: 'net.engio', name: 'mbassador', version: '1.3.2'

```

```xml
<dependency>
    <groupId>net.engio</groupId>
    <artifactId>mbassador</artifactId>
    <version>1.3.2</version>
</dependency>
```

[user_guide](http://www.baeldung.com/mbassador)

##### 6. [Lombok](http://jnb.ociweb.com/jnb/jnbJan2010.html)

```groovy
apply plugin: 'java'
apply plugin: 'nebula.provided-base'

repositories {
	mavenCentral()
}

dependencies {
	provided 'org.projectlombok:lombok:1.16.20'
}
```

```xml
<dependencies>
	<dependency>
		<groupId>org.projectlombok</groupId>
		<artifactId>lombok</artifactId>
		<version>1.16.20</version>
		<scope>provided</scope>
	</dependency>
</dependencies>
```

##### 7. [RXJava] (https://github.com/ReactiveX/RxJava)

```groovy
// https://mvnrepository.com/artifact/io.reactivex.rxjava2/rxjava
compile group: 'io.reactivex.rxjava2', name: 'rxjava', version: '2.1.13'

```

```xml
<!-- https://mvnrepository.com/artifact/io.reactivex.rxjava2/rxjava -->
<dependency>
    <groupId>io.reactivex.rxjava2</groupId>
    <artifactId>rxjava</artifactId>
    <version>2.1.13</version>
</dependency>

```

[user_guide](http://www.vogella.com/tutorials/RxJava/article.html)


##### 8. [Spock](http://spockframework.org/)

```groovy
testCompile "org.spockframework:spock-core:1.1-groovy-2.4-rc-2"
```

```xml
<dependency>
  <groupId>org.spockframework</groupId>
  <artifactId>spock-core</artifactId>
  <version>1.1-groovy-2.4-rc-2</version>
  <scope>test</scope>
</dependency>
```

[user_guide1](http://thejavatar.com/testing-with-spock/#more-71)

[user_guide2](http://www.baeldung.com/groovy-spock)
[user_guide3](https://examples.javacodegeeks.com/core-java/spock-tutorial-beginners/)
