#!/bin/bash

#build docker container
docker build . -t the_hole_service

#run docker container
docker run --restart=always -p5003:5003 --name the_hole_container -d the_hole_service
