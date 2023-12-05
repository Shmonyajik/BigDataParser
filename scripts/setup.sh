echo "Creating network"
docker network create elastic

echo "Building and running elastic + kibana in background"
docker-compose up -d

echo "Waiting for elastic initialization"
sleep 40

echo "Building reindexer"
docker build -t reindexer .

echo "Running reindexing process"
docker run --name reindexer --net elastic reindexer