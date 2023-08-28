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

## HOW TO CONFIGURE

### Complete environment file (from .env.example to .env)

Find client identity on Portal azure to provide docker environment variable

Env variable require 4 credential field: subscription_id, tenant, client_id, secret. That you can find by completing the following steps

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

### Set kubernetes and ansible files

```bash
deploy.yml: ansible File
kubeapplication.yml: kubernetes File
```

## HOW TO DEV

```bash
make build: to build this image
make dev: to run a container
```