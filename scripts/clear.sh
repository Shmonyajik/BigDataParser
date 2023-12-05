docker compose stop
docker stop reindexer

docker network rm elastic

docker compose rm -f
docker rm reindexer