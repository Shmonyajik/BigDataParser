docker stop elasticsearch
docker stop kibana
docker stop reindexer

docker network rm elastic

docker rm elasticsearch
docker rm kibana
docker rm reindexer