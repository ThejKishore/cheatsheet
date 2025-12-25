# Adding a Custom OAuth RestTemplate to Config Server Client

Here's how to implement a custom OAuth-enabled RestTemplate for your Spring Cloud Config client:

## Option 1: Using Config Data (Recommended for Spring Boot 2.4+)

### Step 1: Create the BootstrapRegistryInitializer

```java
package com.my.config.client;

import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.OAuth2AuthorizeRequest;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizedClientRepository;
import org.springframework.web.client.RestTemplate;

public class OAuthConfigClientBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

    @Override
    public void initialize(BootstrapRegistry registry) {
        registry.register(RestTemplate.class, context -> {
            RestTemplate restTemplate = new RestTemplate();
            
            // Add OAuth2 interceptor
            restTemplate.getInterceptors().add((request, body, execution) -> {
                // Add OAuth2 Bearer token to Authorization header
                String token = getOAuth2Token();
                if (token != null) {
                    request.getHeaders().setBearerAuth(token);
                }
                return execution.execute(request, body);
            });
            
            return restTemplate;
        });
    }
    
    private String getOAuth2Token() {
        // Implement OAuth2 token retrieval logic
        // This is a simplified example - you'll need to implement actual OAuth2 flow
        // Consider using OAuth2AuthorizedClientManager for production code
        return System.getProperty("oauth.token"); // Placeholder
    }
}
```

### Step 2: Create spring.factories

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.boot.BootstrapRegistryInitializer=com.my.config.client.OAuthConfigClientBootstrapRegistryInitializer
```

## Option 2: Using Bootstrap (Legacy approach)

### Step 1: Add Dependencies

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-client</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
```

### Step 2: Create Bootstrap Configuration

```java
package com.my.config.client;

import org.springframework.cloud.config.client.ConfigClientProperties;
import org.springframework.cloud.config.client.ConfigServicePropertySourceLocator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.security.oauth2.client.*;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.web.client.RestTemplate;

@Configuration
public class OAuthConfigServiceBootstrapConfiguration {

    @Bean
    public ConfigServicePropertySourceLocator configServicePropertySourceLocator(
            ConfigClientProperties clientProperties) {
        
        ConfigServicePropertySourceLocator locator = 
            new ConfigServicePropertySourceLocator(clientProperties);
        
        locator.setRestTemplate(createOAuthRestTemplate(clientProperties));
        
        return locator;
    }

    @Bean
    public ConfigClientProperties configClientProperties() {
        return new ConfigClientProperties();
    }

    private RestTemplate createOAuthRestTemplate(ConfigClientProperties clientProperties) {
        RestTemplate restTemplate = new RestTemplate();
        
        // Add OAuth2 interceptor
        ClientHttpRequestInterceptor interceptor = (request, body, execution) -> {
            String token = retrieveOAuth2Token();
            if (token != null) {
                request.getHeaders().setBearerAuth(token);
            }
            return execution.execute(request, body);
        };
        
        restTemplate.getInterceptors().add(interceptor);
        
        return restTemplate;
    }
    
    private String retrieveOAuth2Token() {
        // Implement OAuth2 client credentials flow or other OAuth2 flow
        // This would typically use OAuth2AuthorizedClientManager
        return null; // Placeholder
    }
}
```

### Step 3: Create spring.factories for Bootstrap

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.cloud.bootstrap.BootstrapConfiguration=com.my.config.client.OAuthConfigServiceBootstrapConfiguration
```

## Production-Ready OAuth2 Implementation

For a production-ready solution with proper OAuth2 Client Credentials flow:

```java
package com.my.config.client;

import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.security.oauth2.client.*;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;

public class OAuthConfigClientBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

    @Override
    public void initialize(BootstrapRegistry registry) {
        registry.register(RestTemplate.class, context -> {
            RestTemplate restTemplate = new RestTemplate();
            
            // Create OAuth2 client configuration
            ClientRegistration clientRegistration = ClientRegistration
                .withRegistrationId("config-server")
                .clientId(System.getProperty("oauth.client.id", "config-client"))
                .clientSecret(System.getProperty("oauth.client.secret", "secret"))
                .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
                .tokenUri(System.getProperty("oauth.token.uri", "http://localhost:8080/oauth/token"))
                .build();
            
            ClientRegistrationRepository clientRegistrationRepository = 
                new InMemoryClientRegistrationRepository(clientRegistration);
            
            OAuth2AuthorizedClientService authorizedClientService = 
                new InMemoryOAuth2AuthorizedClientService(clientRegistrationRepository);
            
            AuthorizedClientServiceOAuth2AuthorizedClientManager authorizedClientManager = 
                new AuthorizedClientServiceOAuth2AuthorizedClientManager(
                    clientRegistrationRepository, 
                    authorizedClientService
                );
            
            // Add OAuth2 interceptor
            restTemplate.getInterceptors().add(
                new OAuth2ClientHttpRequestInterceptor(authorizedClientManager, "config-server")
            );
            
            return restTemplate;
        });
    }
    
    private static class OAuth2ClientHttpRequestInterceptor implements ClientHttpRequestInterceptor {
        
        private final OAuth2AuthorizedClientManager authorizedClientManager;
        private final String clientRegistrationId;
        
        public OAuth2ClientHttpRequestInterceptor(
                OAuth2AuthorizedClientManager authorizedClientManager,
                String clientRegistrationId) {
            this.authorizedClientManager = authorizedClientManager;
            this.clientRegistrationId = clientRegistrationId;
        }
        
        @Override
        public ClientHttpResponse intercept(HttpRequest request, byte[] body, 
                                            ClientHttpRequestExecution execution) throws IOException {
            OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                .withClientRegistrationId(clientRegistrationId)
                .principal("config-client")
                .build();
            
            OAuth2AuthorizedClient authorizedClient = 
                authorizedClientManager.authorize(authorizeRequest);
            
            if (authorizedClient != null) {
                String tokenValue = authorizedClient.getAccessToken().getTokenValue();
                request.getHeaders().setBearerAuth(tokenValue);
            }
            
            return execution.execute(request, body);
        }
    }
}
```

## Configuration Properties

Add to `application.yml` or `bootstrap.yml`:

```yaml
spring:
  cloud:
    config:
      uri: http://localhost:8888
      # Alternative: Use headers for simple token-based auth
      # headers:
      #   Authorization: Bearer ${OAUTH_TOKEN}
      
# OAuth2 configuration (if using environment variables)
oauth:
  client:
    id: ${OAUTH_CLIENT_ID:config-client}
    secret: ${OAUTH_CLIENT_SECRET:secret}
  token:
    uri: ${OAUTH_TOKEN_URI:http://localhost:8080/oauth/token}
```

This implementation provides a custom OAuth2-enabled RestTemplate that automatically handles token retrieval and adds the Bearer token to all requests made to the Config Server.

# Adding Mutual TLS (mTLS) to Config Server Client RestTemplate

Here's how to implement a custom RestTemplate with mutual TLS authentication for your Spring Cloud Config client:

## Option 1: Using Config Data (Recommended for Spring Boot 2.4+)

### Step 1: Create the BootstrapRegistryInitializer with mTLS

```java
package com.my.config.client;

import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;
import java.io.InputStream;
import java.security.KeyStore;

public class MutualTLSConfigClientBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

    @Override
    public void initialize(BootstrapRegistry registry) {
        registry.register(RestTemplate.class, context -> {
            try {
                RestTemplate restTemplate = new RestTemplate();
                
                // Configure mutual TLS
                SSLContext sslContext = createSSLContext();
                
                SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
                    sslContext,
                    new String[]{"TLSv1.2", "TLSv1.3"},
                    null,
                    // Use NoopHostnameVerifier only for development
                    // For production, use SSLConnectionSocketFactory.getDefaultHostnameVerifier()
                    SSLConnectionSocketFactory.getDefaultHostnameVerifier()
                );
                
                CloseableHttpClient httpClient = HttpClients.custom()
                    .setSSLSocketFactory(socketFactory)
                    .build();
                
                HttpComponentsClientHttpRequestFactory requestFactory = 
                    new HttpComponentsClientHttpRequestFactory(httpClient);
                
                restTemplate.setRequestFactory(requestFactory);
                
                return restTemplate;
                
            } catch (Exception e) {
                throw new RuntimeException("Failed to create mutual TLS RestTemplate", e);
            }
        });
    }
    
    private SSLContext createSSLContext() throws Exception {
        // Load keystore (client certificate and private key)
        String keystorePath = System.getProperty("spring.cloud.config.tls.keystore.path", 
            "classpath:client-keystore.p12");
        String keystorePassword = System.getProperty("spring.cloud.config.tls.keystore.password", 
            "changeit");
        String keystoreType = System.getProperty("spring.cloud.config.tls.keystore.type", "PKCS12");
        
        // Load truststore (trusted CA certificates)
        String truststorePath = System.getProperty("spring.cloud.config.tls.truststore.path", 
            "classpath:client-truststore.p12");
        String truststorePassword = System.getProperty("spring.cloud.config.tls.truststore.password", 
            "changeit");
        String truststoreType = System.getProperty("spring.cloud.config.tls.truststore.type", "PKCS12");
        
        KeyStore keyStore = loadKeyStore(keystorePath, keystorePassword, keystoreType);
        KeyStore trustStore = loadKeyStore(truststorePath, truststorePassword, truststoreType);
        
        return SSLContextBuilder.create()
            .loadKeyMaterial(keyStore, keystorePassword.toCharArray())
            .loadTrustMaterial(trustStore, null)
            .build();
    }
    
    private KeyStore loadKeyStore(String path, String password, String type) throws Exception {
        KeyStore keyStore = KeyStore.getInstance(type);
        
        try (InputStream inputStream = getInputStream(path)) {
            keyStore.load(inputStream, password.toCharArray());
        }
        
        return keyStore;
    }
    
    private InputStream getInputStream(String path) throws Exception {
        if (path.startsWith("classpath:")) {
            String resourcePath = path.substring("classpath:".length());
            Resource resource = new ClassPathResource(resourcePath);
            return resource.getInputStream();
        } else {
            return new java.io.FileInputStream(path);
        }
    }
}
```

### Step 2: Add Required Dependencies

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-config</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.httpcomponents</groupId>
        <artifactId>httpclient</artifactId>
    </dependency>
</dependencies>
```

### Step 3: Create spring.factories

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.boot.BootstrapRegistryInitializer=com.my.config.client.MutualTLSConfigClientBootstrapRegistryInitializer
```

## Option 2: Using Bootstrap (Legacy approach)

### Step 1: Create Bootstrap Configuration

```java
package com.my.config.client;

import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.springframework.cloud.config.client.ConfigClientProperties;
import org.springframework.cloud.config.client.ConfigServicePropertySourceLocator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;
import java.io.InputStream;
import java.security.KeyStore;

@Configuration
public class MutualTLSConfigServiceBootstrapConfiguration {

    @Bean
    public ConfigServicePropertySourceLocator configServicePropertySourceLocator(
            ConfigClientProperties clientProperties) {
        
        ConfigServicePropertySourceLocator locator = 
            new ConfigServicePropertySourceLocator(clientProperties);
        
        locator.setRestTemplate(createMutualTLSRestTemplate());
        
        return locator;
    }

    @Bean
    public ConfigClientProperties configClientProperties() {
        return new ConfigClientProperties();
    }

    private RestTemplate createMutualTLSRestTemplate() {
        try {
            // Load keystore (client certificate and private key)
            KeyStore keyStore = KeyStore.getInstance("PKCS12");
            Resource keystoreResource = new ClassPathResource("client-keystore.p12");
            try (InputStream keystoreStream = keystoreResource.getInputStream()) {
                keyStore.load(keystoreStream, "changeit".toCharArray());
            }
            
            // Load truststore (trusted CA certificates)
            KeyStore trustStore = KeyStore.getInstance("PKCS12");
            Resource truststoreResource = new ClassPathResource("client-truststore.p12");
            try (InputStream truststoreStream = truststoreResource.getInputStream()) {
                trustStore.load(truststoreStream, "changeit".toCharArray());
            }
            
            // Build SSL context
            SSLContext sslContext = SSLContextBuilder.create()
                .loadKeyMaterial(keyStore, "changeit".toCharArray())
                .loadTrustMaterial(trustStore, null)
                .build();
            
            SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
                sslContext,
                new String[]{"TLSv1.2", "TLSv1.3"},
                null,
                SSLConnectionSocketFactory.getDefaultHostnameVerifier()
            );
            
            CloseableHttpClient httpClient = HttpClients.custom()
                .setSSLSocketFactory(socketFactory)
                .build();
            
            HttpComponentsClientHttpRequestFactory requestFactory = 
                new HttpComponentsClientHttpRequestFactory(httpClient);
            
            RestTemplate restTemplate = new RestTemplate(requestFactory);
            
            return restTemplate;
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to create mutual TLS RestTemplate", e);
        }
    }
}
```

### Step 2: Create spring.factories for Bootstrap

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.cloud.bootstrap.BootstrapConfiguration=com.my.config.client.MutualTLSConfigServiceBootstrapConfiguration
```

## Enhanced Version with OAuth2 + Mutual TLS

```java
package com.my.config.client;

import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.io.InputStream;
import java.security.KeyStore;

public class OAuth2MutualTLSConfigClientBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

    @Override
    public void initialize(BootstrapRegistry registry) {
        registry.register(RestTemplate.class, context -> {
            try {
                RestTemplate restTemplate = createMutualTLSRestTemplate();
                
                // Add OAuth2 interceptor
                restTemplate.getInterceptors().add(new OAuth2BearerTokenInterceptor());
                
                return restTemplate;
                
            } catch (Exception e) {
                throw new RuntimeException("Failed to create mutual TLS + OAuth2 RestTemplate", e);
            }
        });
    }
    
    private RestTemplate createMutualTLSRestTemplate() throws Exception {
        // Load certificates
        String keystorePath = System.getProperty("spring.cloud.config.tls.keystore.path", 
            "classpath:client-keystore.p12");
        String keystorePassword = System.getProperty("spring.cloud.config.tls.keystore.password", 
            "changeit");
        String keystoreType = System.getProperty("spring.cloud.config.tls.keystore.type", "PKCS12");
        
        String truststorePath = System.getProperty("spring.cloud.config.tls.truststore.path", 
            "classpath:client-truststore.p12");
        String truststorePassword = System.getProperty("spring.cloud.config.tls.truststore.password", 
            "changeit");
        String truststoreType = System.getProperty("spring.cloud.config.tls.truststore.type", "PKCS12");
        
        KeyStore keyStore = loadKeyStore(keystorePath, keystorePassword, keystoreType);
        KeyStore trustStore = loadKeyStore(truststorePath, truststorePassword, truststoreType);
        
        SSLContext sslContext = SSLContextBuilder.create()
            .loadKeyMaterial(keyStore, keystorePassword.toCharArray())
            .loadTrustMaterial(trustStore, null)
            .build();
        
        SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
            sslContext,
            new String[]{"TLSv1.2", "TLSv1.3"},
            null,
            SSLConnectionSocketFactory.getDefaultHostnameVerifier()
        );
        
        CloseableHttpClient httpClient = HttpClients.custom()
            .setSSLSocketFactory(socketFactory)
            .build();
        
        HttpComponentsClientHttpRequestFactory requestFactory = 
            new HttpComponentsClientHttpRequestFactory(httpClient);
        
        // Set timeouts
        requestFactory.setConnectTimeout(5000);
        requestFactory.setReadTimeout(10000);
        
        return new RestTemplate(requestFactory);
    }
    
    private KeyStore loadKeyStore(String path, String password, String type) throws Exception {
        KeyStore keyStore = KeyStore.getInstance(type);
        
        try (InputStream inputStream = getInputStream(path)) {
            keyStore.load(inputStream, password.toCharArray());
        }
        
        return keyStore;
    }
    
    private InputStream getInputStream(String path) throws Exception {
        if (path.startsWith("classpath:")) {
            String resourcePath = path.substring("classpath:".length());
            Resource resource = new ClassPathResource(resourcePath);
            return resource.getInputStream();
        } else {
            return new java.io.FileInputStream(path);
        }
    }
    
    private static class OAuth2BearerTokenInterceptor implements ClientHttpRequestInterceptor {
        @Override
        public ClientHttpResponse intercept(HttpRequest request, byte[] body, 
                                            ClientHttpRequestExecution execution) throws IOException {
            String token = System.getProperty("oauth.token");
            if (token != null && !token.isEmpty()) {
                request.getHeaders().setBearerAuth(token);
            }
            return execution.execute(request, body);
        }
    }
}
```

## Configuration Properties

Add to `application.yml` or `bootstrap.yml`:

```yaml
spring:
  cloud:
    config:
      uri: https://config-server:8888
      tls:
        enabled: true
        keystore:
          path: classpath:client-keystore.p12
          password: ${KEYSTORE_PASSWORD:changeit}
          type: PKCS12
        truststore:
          path: classpath:client-truststore.p12
          password: ${TRUSTSTORE_PASSWORD:changeit}
          type: PKCS12
```

## Certificate Generation (for testing)

```bash
# Generate server keystore
keytool -genkeypair -alias config-server -keyalg RSA -keysize 2048 \
  -storetype PKCS12 -keystore server-keystore.p12 -validity 365 \
  -dname "CN=config-server,OU=Dev,O=MyCompany,L=City,ST=State,C=US" \
  -storepass changeit

# Export server certificate
keytool -exportcert -alias config-server -keystore server-keystore.p12 \
  -storetype PKCS12 -storepass changeit -file server-cert.cer

# Generate client keystore
keytool -genkeypair -alias config-client -keyalg RSA -keysize 2048 \
  -storetype PKCS12 -keystore client-keystore.p12 -validity 365 \
  -dname "CN=config-client,OU=Dev,O=MyCompany,L=City,ST=State,C=US" \
  -storepass changeit

# Export client certificate
keytool -exportcert -alias config-client -keystore client-keystore.p12 \
  -storetype PKCS12 -storepass changeit -file client-cert.cer

# Create client truststore and import server certificate
keytool -importcert -alias config-server -file server-cert.cer \
  -keystore client-truststore.p12 -storetype PKCS12 -storepass changeit -noprompt

# Create server truststore and import client certificate
keytool -importcert -alias config-client -file client-cert.cer \
  -keystore server-truststore.p12 -storetype PKCS12 -storepass changeit -noprompt
```

Place `client-keystore.p12` and `client-truststore.p12` in `src/main/resources/`.

This implementation provides a production-ready mutual TLS configuration for your Config Server client.

# Adding Mutual TLS for OAuth2 Token Fetching

Here's how to implement a custom RestTemplate with mutual TLS specifically for OAuth2 token retrieval, while using standard HTTPS for the Config Server:

## Option 1: Using Config Data (Recommended for Spring Boot 2.4+)

### Step 1: Create the BootstrapRegistryInitializer with mTLS OAuth2

```java
package com.my.config.client;

import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.security.oauth2.client.*;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.io.InputStream;
import java.security.KeyStore;

public class OAuth2MutualTLSConfigClientBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

    @Override
    public void initialize(BootstrapRegistry registry) {
        registry.register(RestTemplate.class, context -> {
            try {
                // Create RestTemplate for Config Server (standard HTTPS)
                RestTemplate configServerRestTemplate = new RestTemplate();
                
                // Create OAuth2 client manager with mTLS RestTemplate for token endpoint
                OAuth2AuthorizedClientManager authorizedClientManager = 
                    createOAuth2ClientManager();
                
                // Add OAuth2 interceptor to Config Server RestTemplate
                configServerRestTemplate.getInterceptors().add(
                    new OAuth2ClientHttpRequestInterceptor(authorizedClientManager, "config-server")
                );
                
                return configServerRestTemplate;
                
            } catch (Exception e) {
                throw new RuntimeException("Failed to create OAuth2 mTLS RestTemplate", e);
            }
        });
    }
    
    private OAuth2AuthorizedClientManager createOAuth2ClientManager() throws Exception {
        // Create mTLS RestTemplate for OAuth2 token endpoint
        RestTemplate oauth2RestTemplate = createMutualTLSRestTemplate();
        
        // Create client registration
        ClientRegistration clientRegistration = ClientRegistration
            .withRegistrationId("config-server")
            .clientId(System.getProperty("oauth.client.id", "config-client"))
            .clientSecret(System.getProperty("oauth.client.secret", "secret"))
            .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
            .tokenUri(System.getProperty("oauth.token.uri", "https://auth-server:8443/oauth/token"))
            .scope(System.getProperty("oauth.scope", "config.read"))
            .build();
        
        ClientRegistrationRepository clientRegistrationRepository = 
            new InMemoryClientRegistrationRepository(clientRegistration);
        
        OAuth2AuthorizedClientService authorizedClientService = 
            new InMemoryOAuth2AuthorizedClientService(clientRegistrationRepository);
        
        // Create custom provider with mTLS RestTemplate
        OAuth2AccessTokenResponseClient<OAuth2ClientCredentialsGrantRequest> accessTokenResponseClient =
            new CustomMutualTLSOAuth2AccessTokenResponseClient(oauth2RestTemplate);
        
        // Create provider with custom token response client
        OAuth2AuthorizedClientProvider authorizedClientProvider = 
            OAuth2AuthorizedClientProviderBuilder.builder()
                .clientCredentials(configurer -> 
                    configurer.accessTokenResponseClient(accessTokenResponseClient))
                .build();
        
        AuthorizedClientServiceOAuth2AuthorizedClientManager authorizedClientManager = 
            new AuthorizedClientServiceOAuth2AuthorizedClientManager(
                clientRegistrationRepository, 
                authorizedClientService
            );
        
        authorizedClientManager.setAuthorizedClientProvider(authorizedClientProvider);
        
        return authorizedClientManager;
    }
    
    private RestTemplate createMutualTLSRestTemplate() throws Exception {
        // Load keystore (client certificate and private key)
        String keystorePath = System.getProperty("oauth.tls.keystore.path", 
            "classpath:oauth-client-keystore.p12");
        String keystorePassword = System.getProperty("oauth.tls.keystore.password", 
            "changeit");
        String keystoreType = System.getProperty("oauth.tls.keystore.type", "PKCS12");
        
        // Load truststore (trusted CA certificates)
        String truststorePath = System.getProperty("oauth.tls.truststore.path", 
            "classpath:oauth-client-truststore.p12");
        String truststorePassword = System.getProperty("oauth.tls.truststore.password", 
            "changeit");
        String truststoreType = System.getProperty("oauth.tls.truststore.type", "PKCS12");
        
        KeyStore keyStore = loadKeyStore(keystorePath, keystorePassword, keystoreType);
        KeyStore trustStore = loadKeyStore(truststorePath, truststorePassword, truststoreType);
        
        SSLContext sslContext = SSLContextBuilder.create()
            .loadKeyMaterial(keyStore, keystorePassword.toCharArray())
            .loadTrustMaterial(trustStore, null)
            .build();
        
        SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
            sslContext,
            new String[]{"TLSv1.2", "TLSv1.3"},
            null,
            SSLConnectionSocketFactory.getDefaultHostnameVerifier()
        );
        
        CloseableHttpClient httpClient = HttpClients.custom()
            .setSSLSocketFactory(socketFactory)
            .build();
        
        HttpComponentsClientHttpRequestFactory requestFactory = 
            new HttpComponentsClientHttpRequestFactory(httpClient);
        
        // Set timeouts for token endpoint
        requestFactory.setConnectTimeout(5000);
        requestFactory.setReadTimeout(10000);
        
        return new RestTemplate(requestFactory);
    }
    
    private KeyStore loadKeyStore(String path, String password, String type) throws Exception {
        KeyStore keyStore = KeyStore.getInstance(type);
        
        try (InputStream inputStream = getInputStream(path)) {
            keyStore.load(inputStream, password.toCharArray());
        }
        
        return keyStore;
    }
    
    private InputStream getInputStream(String path) throws Exception {
        if (path.startsWith("classpath:")) {
            String resourcePath = path.substring("classpath:".length());
            Resource resource = new ClassPathResource(resourcePath);
            return resource.getInputStream();
        } else {
            return new java.io.FileInputStream(path);
        }
    }
    
    // Custom OAuth2 token response client that uses mTLS RestTemplate
    private static class CustomMutualTLSOAuth2AccessTokenResponseClient 
            implements OAuth2AccessTokenResponseClient<OAuth2ClientCredentialsGrantRequest> {
        
        private final RestTemplate restTemplate;
        
        public CustomMutualTLSOAuth2AccessTokenResponseClient(RestTemplate restTemplate) {
            this.restTemplate = restTemplate;
        }
        
        @Override
        public OAuth2AccessTokenResponse getTokenResponse(
                OAuth2ClientCredentialsGrantRequest authorizationGrantRequest) {
            
            // Use Spring Security's default implementation but with custom RestTemplate
            org.springframework.security.oauth2.client.endpoint.DefaultClientCredentialsTokenResponseClient client = 
                new org.springframework.security.oauth2.client.endpoint.DefaultClientCredentialsTokenResponseClient();
            
            client.setRestOperations(restTemplate);
            
            return client.getTokenResponse(authorizationGrantRequest);
        }
    }
    
    // Interceptor to add OAuth2 token to Config Server requests
    private static class OAuth2ClientHttpRequestInterceptor implements ClientHttpRequestInterceptor {
        
        private final OAuth2AuthorizedClientManager authorizedClientManager;
        private final String clientRegistrationId;
        
        public OAuth2ClientHttpRequestInterceptor(
                OAuth2AuthorizedClientManager authorizedClientManager,
                String clientRegistrationId) {
            this.authorizedClientManager = authorizedClientManager;
            this.clientRegistrationId = clientRegistrationId;
        }
        
        @Override
        public ClientHttpResponse intercept(HttpRequest request, byte[] body, 
                                            ClientHttpRequestExecution execution) throws IOException {
            OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                .withClientRegistrationId(clientRegistrationId)
                .principal("config-client")
                .build();
            
            OAuth2AuthorizedClient authorizedClient = 
                authorizedClientManager.authorize(authorizeRequest);
            
            if (authorizedClient != null) {
                String tokenValue = authorizedClient.getAccessToken().getTokenValue();
                request.getHeaders().setBearerAuth(tokenValue);
            }
            
            return execution.execute(request, body);
        }
    }
}
```

### Step 2: Add Required Dependencies

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-config</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.security</groupId>
        <artifactId>spring-security-oauth2-client</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.httpcomponents</groupId>
        <artifactId>httpclient</artifactId>
    </dependency>
</dependencies>
```

### Step 3: Create spring.factories

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.boot.BootstrapRegistryInitializer=com.my.config.client.OAuth2MutualTLSConfigClientBootstrapRegistryInitializer
```

## Option 2: Using Bootstrap (Legacy approach)

### Step 1: Create Bootstrap Configuration

```java
package com.my.config.client;

import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.springframework.cloud.config.client.ConfigClientProperties;
import org.springframework.cloud.config.client.ConfigServicePropertySourceLocator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.security.oauth2.client.*;
import org.springframework.security.oauth2.client.endpoint.DefaultClientCredentialsTokenResponseClient;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.io.InputStream;
import java.security.KeyStore;

@Configuration
public class OAuth2MutualTLSConfigServiceBootstrapConfiguration {

    @Bean
    public ConfigServicePropertySourceLocator configServicePropertySourceLocator(
            ConfigClientProperties clientProperties) {
        
        ConfigServicePropertySourceLocator locator = 
            new ConfigServicePropertySourceLocator(clientProperties);
        
        locator.setRestTemplate(createConfigServerRestTemplate());
        
        return locator;
    }

    @Bean
    public ConfigClientProperties configClientProperties() {
        return new ConfigClientProperties();
    }

    private RestTemplate createConfigServerRestTemplate() {
        try {
            // Standard RestTemplate for Config Server
            RestTemplate configServerRestTemplate = new RestTemplate();
            
            // Create OAuth2 client manager with mTLS
            OAuth2AuthorizedClientManager authorizedClientManager = 
                createOAuth2ClientManager();
            
            // Add OAuth2 interceptor
            configServerRestTemplate.getInterceptors().add(
                new OAuth2ClientHttpRequestInterceptor(authorizedClientManager, "config-server")
            );
            
            return configServerRestTemplate;
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to create OAuth2 mTLS RestTemplate", e);
        }
    }
    
    private OAuth2AuthorizedClientManager createOAuth2ClientManager() throws Exception {
        // Create mTLS RestTemplate for OAuth2 token endpoint
        RestTemplate oauth2RestTemplate = createMutualTLSRestTemplate();
        
        // Client registration
        ClientRegistration clientRegistration = ClientRegistration
            .withRegistrationId("config-server")
            .clientId("config-client")
            .clientSecret("secret")
            .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
            .tokenUri("https://auth-server:8443/oauth/token")
            .scope("config.read")
            .build();
        
        ClientRegistrationRepository clientRegistrationRepository = 
            new InMemoryClientRegistrationRepository(clientRegistration);
        
        OAuth2AuthorizedClientService authorizedClientService = 
            new InMemoryOAuth2AuthorizedClientService(clientRegistrationRepository);
        
        // Create token response client with mTLS RestTemplate
        DefaultClientCredentialsTokenResponseClient tokenResponseClient = 
            new DefaultClientCredentialsTokenResponseClient();
        tokenResponseClient.setRestOperations(oauth2RestTemplate);
        
        // Configure provider
        OAuth2AuthorizedClientProvider authorizedClientProvider = 
            OAuth2AuthorizedClientProviderBuilder.builder()
                .clientCredentials(configurer -> 
                    configurer.accessTokenResponseClient(tokenResponseClient))
                .build();
        
        AuthorizedClientServiceOAuth2AuthorizedClientManager authorizedClientManager = 
            new AuthorizedClientServiceOAuth2AuthorizedClientManager(
                clientRegistrationRepository, 
                authorizedClientService
            );
        
        authorizedClientManager.setAuthorizedClientProvider(authorizedClientProvider);
        
        return authorizedClientManager;
    }
    
    private RestTemplate createMutualTLSRestTemplate() throws Exception {
        // Load keystore
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        Resource keystoreResource = new ClassPathResource("oauth-client-keystore.p12");
        try (InputStream keystoreStream = keystoreResource.getInputStream()) {
            keyStore.load(keystoreStream, "changeit".toCharArray());
        }
        
        // Load truststore
        KeyStore trustStore = KeyStore.getInstance("PKCS12");
        Resource truststoreResource = new ClassPathResource("oauth-client-truststore.p12");
        try (InputStream truststoreStream = truststoreResource.getInputStream()) {
            trustStore.load(truststoreStream, "changeit".toCharArray());
        }
        
        // Build SSL context with mutual TLS
        SSLContext sslContext = SSLContextBuilder.create()
            .loadKeyMaterial(keyStore, "changeit".toCharArray())
            .loadTrustMaterial(trustStore, null)
            .build();
        
        SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
            sslContext,
            new String[]{"TLSv1.2", "TLSv1.3"},
            null,
            SSLConnectionSocketFactory.getDefaultHostnameVerifier()
        );
        
        CloseableHttpClient httpClient = HttpClients.custom()
            .setSSLSocketFactory(socketFactory)
            .build();
        
        HttpComponentsClientHttpRequestFactory requestFactory = 
            new HttpComponentsClientHttpRequestFactory(httpClient);
        
        requestFactory.setConnectTimeout(5000);
        requestFactory.setReadTimeout(10000);
        
        return new RestTemplate(requestFactory);
    }
    
    private static class OAuth2ClientHttpRequestInterceptor implements ClientHttpRequestInterceptor {
        
        private final OAuth2AuthorizedClientManager authorizedClientManager;
        private final String clientRegistrationId;
        
        public OAuth2ClientHttpRequestInterceptor(
                OAuth2AuthorizedClientManager authorizedClientManager,
                String clientRegistrationId) {
            this.authorizedClientManager = authorizedClientManager;
            this.clientRegistrationId = clientRegistrationId;
        }
        
        @Override
        public ClientHttpResponse intercept(HttpRequest request, byte[] body, 
                                            ClientHttpRequestExecution execution) throws IOException {
            OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                .withClientRegistrationId(clientRegistrationId)
                .principal("config-client")
                .build();
            
            OAuth2AuthorizedClient authorizedClient = 
                authorizedClientManager.authorize(authorizeRequest);
            
            if (authorizedClient != null) {
                String tokenValue = authorizedClient.getAccessToken().getTokenValue();
                request.getHeaders().setBearerAuth(tokenValue);
            }
            
            return execution.execute(request, body);
        }
    }
}
```

### Step 2: Create spring.factories for Bootstrap

Create `src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.cloud.bootstrap.BootstrapConfiguration=com.my.config.client.OAuth2MutualTLSConfigServiceBootstrapConfiguration
```

## Configuration Properties

Add to `application.yml` or `bootstrap.yml`:

```yaml
spring:
  cloud:
    config:
      uri: https://config-server:8888
      # Config Server uses standard HTTPS (no client cert required)

# OAuth2 configuration with mTLS
oauth:
  client:
    id: ${OAUTH_CLIENT_ID:config-client}
    secret: ${OAUTH_CLIENT_SECRET:secret}
  token:
    uri: ${OAUTH_TOKEN_URI:https://auth-server:8443/oauth/token}
  scope: config.read
  tls:
    keystore:
      path: classpath:oauth-client-keystore.p12
      password: ${OAUTH_KEYSTORE_PASSWORD:changeit}
      type: PKCS12
    truststore:
      path: classpath:oauth-client-truststore.p12
      password: ${OAUTH_TRUSTSTORE_PASSWORD:changeit}
      type: PKCS12
```

## Certificate Setup

Place these files in `src/main/resources/`:
- `oauth-client-keystore.p12` - Contains client certificate and private key for OAuth2 server authentication
- `oauth-client-truststore.p12` - Contains trusted CA certificates for OAuth2 server

## Flow Diagram

```
1. Config Client starts up
2. Needs to fetch configuration from Config Server
3. First, obtains OAuth2 token:
   - Creates mTLS connection to OAuth2 token endpoint
   - Presents client certificate during TLS handshake
   - Receives access token
4. Then, connects to Config Server:
   - Uses standard HTTPS (no client cert)
   - Includes Bearer token in Authorization header
5. Config Server validates token and returns configuration
```

This setup ensures mutual TLS is used only for OAuth2 token fetching, while the Config Server connection uses standard HTTPS with Bearer token authentication.
