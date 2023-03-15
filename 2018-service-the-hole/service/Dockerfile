FROM debian:stretch

WORKDIR /app

RUN apt-get update -qq
RUN apt-get install -y g++

COPY main.cpp /app/server.cpp

RUN g++ server.cpp -lpthread -o server

EXPOSE 5003

CMD ["./server"]
