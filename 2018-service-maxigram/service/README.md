check it
# maxigram

# Docker user manual
# Install docker
```
sudo apt-get install docker
```
# Build database and server images
```
docker build database -t max_db
docker build server -t max_serv
```
# Run database container
```
docker run --name max_db --rm max_db
```
# Run server container
```
docker run --name max_serv --link max_db:max_db -p 8888:8888 --rm max_serv
```

## About

simple Python chat with sockets and GUI
## Install

Install tkinter:
```
sudo apt-get install python3-tk
OR 
sudo apt-get install tk
```

Client:

```
python3 maxigram.py
```
OR
```
./maxigram.py
```

## Useful

Install virtualenv:

```
sudo pip3 install virtualenv
```

Create virtual enironment:

```
virtualenv <name_venv>
```

Activate virtual environment:

```
source <name_venv>/bin/activate
```
