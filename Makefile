#!make
VERSION=$(shell git rev-parse --short HEAD)
APP_NAME=ansibledind
DOCKER_REPO=maissacrement

env ?= .env
-include $(env)
export $(shell sed 's/=.*//' $(env))

version:
	@echo $(VERSION)

login:
	@docker login $(DOCKER_REPO)

build:
	@docker build -t $(APP_NAME) .

dev:
	@docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock --name $(APP_NAME) --env-file=.env $(APP_NAME)

tag-latest:
	@echo 'create tag latest'
	@docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):latest

tag-version:
	@echo 'create tag $(VERSION)'
	@docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):$(VERSION)

push: version build tag-version tag-latest
	@echo 'publish $(VERSION) to $(DOCKER_REPO)'
	@docker push $(DOCKER_REPO)/$(APP_NAME):$(VERSION)
	@docker push $(DOCKER_REPO)/$(APP_NAME):latest