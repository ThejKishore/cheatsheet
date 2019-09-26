
## create primary seed node:
docker run --name cas1 -p 9042:9042 -e CASSANDRA_CLUSTER_NAME=MyCluster -e CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch -e CASSANDRA_DC=datacenter1 -d cassandra

## inspect seed node
docker inspect --format='{{ .NetworkSettings.IPAddress }}' cas1


## create secondary seed.
docker run --name cas2 -e CASSANDRA_SEEDS="$(docker inspect --format='{{ .NetworkSettings.IPAddress }}' cas1)" -e CASSANDRA_CLUSTER_NAME=MyCluster -e CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch -e CASSANDRA_DC=datacenter1 -d cassandra
 
## create secondary seed: 
docker run --name cas3 -e CASSANDRA_SEEDS="$(docker inspect --format='{{ .NetworkSettings.IPAddress }}' cas1)" -e CASSANDRA_CLUSTER_NAME=MyCluster -e CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch -e CASSANDRA_DC=datacenter1 -d cassandra


## validate to see if the all nodes are up

docker ps


## run node tool to see if other node connects...


docker exec -ti cas1 nodetool status


## login and execute the cql commands

docker exec -ti cas1 cqlsh
docker exec -ti cas2 cqlsh
docker exec -ti cas3 cqlsh


### to run the file

SOURCE '/mydir/myfile.cql'
