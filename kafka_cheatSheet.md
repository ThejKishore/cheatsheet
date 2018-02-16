
#### Apache Kafka Server

1. Start the zookeeper.


```bash
cd kafka_2.11
sh bin/zookeeper-server-start.sh config/zookeeper.properties
```

2. Start the kafka server

```bash
cd kafka_2.11
sh bin/kafka-server-start.sh config/server.properties
```

3. create Topic

```bash
cd kafka_2.11/bin
sh kafka-topic.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic testtopic
```

4. create producer for testing topic

```bash
cd kafka_2.11/bin
sh kafka-console-producer.sh --broker-list localhost:9092 --topic testtopic
```

5. create consumer for testig topic

```bash
cd kafka_2.11/bin
sh kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic testtopic --from-beginning 
```