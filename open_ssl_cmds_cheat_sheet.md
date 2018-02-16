
#### creating pub cert and private cert as pem
```
openssl req -subj '/C=US/ST=Illinois/L=Chicago/O=self/OU=home/CN=localhost' -nodes -x509 -sha256 -newkey rsa:4096 -keyout ${private_key_file} -out ${pub_key_file} -days 800
```

#### bundling pem cert  to pkcs12
```
openssl pkcs12 -export -in ${public_cert} -inkey ${private_cert} -out ${consolidated_p12} -name "${alias_name}"
``````

#### converting pkcs12 to pem
```
openssl pkcs12 -in ${filename.p12} -out ${filename}.pem
```

#### Displaying x509 text from pem
```
openssl x509 -text -in ${filename}.pem

openssl x509 -text -pubkey -in ${filename}.pem

openssl rsa -in ${filename}.pem -pubout
```
