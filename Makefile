UID := $(shell id -u)
GID := $(shell id -g)


build:
	docker build -t open-cities:0.1 --build-arg "USER_UID=${UID}" .

start:
	docker-compose up -d

install:
	docker exec -it open-cities-dev pip install -r requirements.txt --user