#!/bin/sh

docker stop gracio_pygrid2vecs_instance
docker rm gracio_pygrid2vecs_instance
docker run --name gracio_pygrid2vecs_instance -d gracio_pygrid2vecs
docker logs -f gracio_pygrid2vecs_instance