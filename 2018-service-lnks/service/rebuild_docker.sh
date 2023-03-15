#!/bin/sh

./clean.sh
./remove_docker.sh

docker rm -f wtf_lnks
docker rmi "sibirctf2018:service-lnks"
docker build --rm=true -t "sibirctf2018:service-lnks" ./
docker run -d -p 3154:3154 --name=wtf_lnks "sibirctf2018:service-lnks"