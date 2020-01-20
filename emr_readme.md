## 
```bash
#!/bin/bash

## Script to replace the guava jar
SRC_DIR=${1:-/usr/lib/spark/jars}
SRC_DIR2=${2:-s3://thej-personal/code/guava-17.0.jar}
# SRC_DIR=${1:-/Users/thej/aws/emr/spark/libs}
# SRC_DIR2=${2:-/Users/thej/aws/emr/spark/backup-libs/guava-17.0.jar}

LIB_REPL=`ls $SRC_DIR | grep -E '^guava'`
if [ $? -eq 0 ]
  then
    SRC_FILE="$SRC_DIR/$LIB_REPL"
    echo $SRC_FILE
    sudo sh -c  "mv $SRC_FILE  guava.jar.txt"
    sudo sh -c  "aws s3 cp $SRC_DIR2 $SRC_DIR"
fi

# sudo sh -c 'aws s3 cp s3://thej-personal/script/replace_guava.sh /home/hadoop'
```

```properties
spark.driver.userClassPathFirst=true
spark.executor.userClassPathFirst=true
```






## spark-defualts.conf
```properties
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

spark.master                     yarn
spark.driver.extraClassPath      :/usr/lib/hadoop-lzo/lib/*:/usr/lib/hadoop/hadoop-aws.jar:/usr/share/aws/aws-java-sdk/*:/usr/share/aws/emr/emrfs/conf:/usr/share/aws/emr/emrfs/lib/*:/usr/share/aws/emr/emrfs/auxlib/*:/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/usr/share/aws/emr/security/conf:/usr/share/aws/emr/security/lib/*:/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar
spark.driver.extraLibraryPath    /usr/lib/hadoop/lib/native:/usr/lib/hadoop-lzo/lib/native
spark.executor.extraClassPath    :/usr/lib/hadoop-lzo/lib/*:/usr/lib/hadoop/hadoop-aws.jar:/usr/share/aws/aws-java-sdk/*:/usr/share/aws/emr/emrfs/conf:/usr/share/aws/emr/emrfs/lib/*:/usr/share/aws/emr/emrfs/auxlib/*:/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/usr/share/aws/emr/security/conf:/usr/share/aws/emr/security/lib/*:/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar
spark.executor.extraLibraryPath  /usr/lib/hadoop/lib/native:/usr/lib/hadoop-lzo/lib/native
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs:///var/log/spark/apps
spark.history.fs.logDirectory    hdfs:///var/log/spark/apps
spark.sql.warehouse.dir          hdfs:///user/spark/warehouse
spark.sql.hive.metastore.sharedPrefixes com.amazonaws.services.dynamodbv2
spark.yarn.historyServer.address ip-172-31-84-2.ec2.internal:18080
spark.history.ui.port            18080
spark.shuffle.service.enabled    true
spark.driver.extraJavaOptions    -XX:+UseConcMarkSweepGC -XX:CMSInitiatingOccupancyFraction=70 -XX:MaxHeapFreeRatio=70 -XX:+CMSClassUnloadingEnabled -XX:OnOutOfMemoryError='kill -9 %p'
spark.dynamicAllocation.enabled  true
spark.blacklist.decommissioning.enabled true
spark.blacklist.decommissioning.timeout 1h
spark.resourceManager.cleanupExpiredHost true
spark.stage.attempt.ignoreOnDecommissionFetchFailure true
spark.decommissioning.timeout.threshold 20
spark.executor.extraJavaOptions  -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+UseConcMarkSweepGC -XX:CMSInitiatingOccupancyFraction=70 -XX:MaxHeapFreeRatio=70 -XX:+CMSClassUnloadingEnabled -XX:OnOutOfMemoryError='kill -9 %p'
spark.hadoop.yarn.timeline-service.enabled false
spark.yarn.appMasterEnv.SPARK_PUBLIC_DNS $(hostname -f)
spark.files.fetchFailure.unRegisterOutputOnHost true
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version.emr_internal_use_only.EmrFileSystem 2
spark.hadoop.mapreduce.fileoutputcommitter.cleanup-failures.ignored.emr_internal_use_only.EmrFileSystem true
spark.hadoop.fs.s3.getObject.initialSocketTimeoutMilliseconds 2000
spark.sql.parquet.output.committer.class com.amazon.emr.committer.EmrOptimizedSparkSqlParquetOutputCommitter
spark.sql.parquet.fs.optimized.committer.optimization-enabled true
spark.sql.emr.internal.extensions com.amazonaws.emr.spark.EmrSparkSessionExtensions
spark.executor.memory            4743M
spark.executor.cores             4
spark.yarn.executor.memoryOverheadFactor 0.1875
spark.driver.memory              2048M
###
# /usr/lib/spark/jars
###

```
