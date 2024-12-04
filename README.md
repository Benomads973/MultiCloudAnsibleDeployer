## DEPLOYING A KUBERNETES PROJECT ON JENKINS VIA ANSIBLE TO AZURE (AKS)

## IMAGE

```yaml
image: docker.io/maissacrement/ansibledind
```
[download](https://hub.docker.com/repository/docker/maissacrement/ansibledind/general)

## HOW TO USE

Modify kubernetes and ansible file:

`make dev` or `docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock -e "subscription_id=$subscription_id" -e "client_id=$client_id" -e "secret=$secret" -e "tenant=$tenant" docker.io/maissacrement/ansibledind "ansible-playbook /home/deploy.yml"`

## DOCKER API

[install](https://docs.docker.com/engine/install/)

[post_install](https://docs.docker.com/engine/install/linux-postinstall)

## HOW TO CONFIGURE: Complete environment file (from .env.example to .env)

There are 2 connection modes. The student mode is done via email password.

```bash
email: <azure login email> 
password: <azure login password>
```

And the subscription mode by application. Find client identity on Azure Portal to provide a Docker environment variable.

Environment variables require 4 credential fields: subscription_id, tenant, client_id, secret. That you can find by completing the following steps:

Etape 1:

Run cloud shell, start: `ac account show`, the prompter will display a JSON

```yaml
subscription_id: <'id' field>
tenant: <'tenantId' field>
```

Etape 2:

Select "App registration || Inscriptions d'applications"

Create a new application on "Register application || Inscrire une application" or use an existing Application

Select or enter in an Application on "overview || vue d'ensemble", in the left menu you will see a "Bases" tab

```yaml
client_id: <'Application (client) ID || ID d'application (client)' field> 
```

Click on "Certificats & secrets" and create a new secret with "New client secret || Nouveau secret client" from "Secret ID || ID de secret"

```yaml
secret: <'value || valeur' field> # Get secret value
```

## How to use

### Make (stable vs V1)

Deux images aux choix pour vos tests "stable" ou "v1"

```bash
# Docker version stable
make build-stable # construire l'image (Nom de l'image local /ansibledind-stable)
make dev-stable # lancer le demon de l'image docker en background et s'y attacher sous bash
```

or

```bash
# Docker v1
make build # construire l'image (Nom de l'image local /ansibledind)
make dev # lancer le demon de l'image docker en background et s'y attacher sous bash
```

### Lancement manuel

```bash
# depuis le repertoire courrant
docker build -t ansible-v1 . -f ./docker/V1/Dockerfile
docker run -d -v "./ansible:/home/ansible" -v /var/run/docker.sock:/var/run/docker.sock --name ansible-v1 --env-file=$(env) ansible-v1
docker exec -it /ansible-v1 /bin/bash
```


### Set kubernetes and ansible files

```bash
deploy.yml: ansible File
kubeapplication.yml: kubernetes File
```

## ISSUE

- Mettre en place une TOOLBOX
