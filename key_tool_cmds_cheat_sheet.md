### Creating public and private key cert ###
====================================================
```jshelllanguage
keytool -genkeypair -dname "cn=localhost,ou=home,o=self,c=US" -alias redisDb -keypass ${password} -keystore ${filename} -storepass ${password} -validity 360

or

keytool -genkey -alias redisDb -keyalg RSA -keystore ${filename} -storepass ${password} -keysize 2048
```

#### exporting cert to a file ####
```jshelllanguage
keytool -export -keystore ${source_filename} -alias ${alias_name} -file ${dest_file_name}.cer
```


##### printing cert from key store 
```jshelllanguage
keytool -list -alias ${alias_name} -v -keystore ${filename} -storepass ${password}

keytool -list -alias ${alias_name} -rfc -keystore ${filename} -storepass ${password}
```

#### printing cert from cer file

```jshelllanguage
keytool -printcert -alias ${aliasname} -rfc -file ${filename} -storepass ${password}


keytool -printcert -alias ${aliasname} -v -file ${filename} -storepass ${password}
```

#### importing cert to trustore 
```jshelllanguage
keytool -import -trustcacerts -noprompt -alias ${aliasname} -file ${filename} -keystore ${filename} -storepass ${password}
```
 
#### changing from jks to pkcs12
The JKS keystore uses a proprietary format. It is recommended to migrate to PKCS12 which is an industry standard format using 
```
keytool -importkeystore -srckeystore ssl-server.jks -destkeystore ssl-server.jks -deststoretype pkcs12
```
