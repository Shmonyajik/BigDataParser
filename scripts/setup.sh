echo "Creating network"
docker network create elastic

echo "Building and running elastic in background"
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.12.0
docker run -d --name elasticsearch --net elastic -p 9200:9200 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:7.12.0

echo "Building and running kibana in background"
docker pull docker.elastic.co/kibana/kibana:7.12.0
docker run -d --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:7.12.0

echo "Waiting for elastic initialization"
sleep 30

echo "Building reindexer"
docker build -t reindexer .

echo "Running reindexing process"
docker run --name reindexer --net elastic reindexer