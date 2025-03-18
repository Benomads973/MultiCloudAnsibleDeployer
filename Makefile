SHELL := /bin/bash
VERSION := $(shell git rev-parse --short HEAD)
APP_NAME := ansibledind
DOCKER_REPO := docker.io/maissacrement

env ?= .env
-include $(env)
export $(shell sed 's/=.*//' $(env))

# Détecter le système d'exploitation pour gérer les différences entre Windows, Linux, macOS
OS := $(shell uname -s)

ifdef ComSpec
# Si la variable ComSpec est définie, il s'agit de Windows
DOCKER_SOCK := //var/run/docker.sock
PWD := $(shell pwd -W)
else
# Sinon, c'est macOS ou Linux
DOCKER_SOCK := /var/run/docker.sock
PWD := $(shell pwd)
endif

# Versions Docker
DEFAULT_VERSION := v1  # Version par défaut

# Si aucune version n'est spécifiée, utiliser la version par défaut
TARGET_VERSION ?= $(DEFAULT_VERSION)

version:
	@echo $(VERSION)

login:
	@docker login docker.io

# Règles dynamiques pour build, daemon, dev, etc.
# Génération explicite des règles pour chaque version
build-%:
	@docker build -t $(APP_NAME)-$* . -f ./docker/$*/Dockerfile

daemon-%:
	@docker run -d \
		-v "$(PWD)/ansible:/home/ansible" \
		-v $(DOCKER_SOCK):/var/run/docker.sock --name $(APP_NAME)-$* --env-file=$(env) $(APP_NAME)-$*

dev-%: daemon-%
	@docker exec -it $(APP_NAME)-$* /bin/bash

clean-%:
	@docker rm -f $(APP_NAME)-$* 2>/dev/null || true

tag-%-latest:
	@echo 'create tag latest for $*'
	@docker tag $(APP_NAME)-$* $(DOCKER_REPO)/$(APP_NAME):latest-$*

tag-%-version:
	@echo 'create tag $(VERSION) for $*'
	@docker tag $(APP_NAME)-$* $(DOCKER_REPO)/$(APP_NAME):$(VERSION)-$*

push-%: build-% tag-%-version tag-%-latest
	@echo 'publish $(VERSION) of $* to $(DOCKER_REPO)'
	@docker push $(DOCKER_REPO)/$(APP_NAME):$(VERSION)-$*
	@docker push $(DOCKER_REPO)/$(APP_NAME):latest-$*

prod-%:
	@docker run -it --rm $(DOCKER_REPO)/$(APP_NAME):$(VERSION)-$*

# Génération des règles pour chaque version
$(foreach version, $(VERSIONS), $(eval $(call RULES,$(version))))

# Alias pour utiliser la version par défaut
build: build-$(TARGET_VERSION)
daemon: daemon-$(TARGET_VERSION)
dev: dev-$(TARGET_VERSION)
clean: clean-$(TARGET_VERSION)
tag-latest: tag-$(TARGET_VERSION)-latest
tag-version: tag-$(TARGET_VERSION)-version
push: push-$(TARGET_VERSION)

# Règles globales
clean-all:
	$(foreach version, $(VERSIONS), $(MAKE) clean-$(version);)

push-all:
	$(foreach version, $(VERSIONS), $(MAKE) push-$(version);)
