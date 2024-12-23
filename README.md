## DEPLOYING A KUBERNETES PROJECT ON JENKINS VIA ANSIBLE TO AZURE (AKS)

## IMAGE

```yaml
image: docker.io/maissacrement/ansibledind:4f3419c-stable
```
[download](https://hub.docker.com/repository/docker/maissacrement/ansibledind/general)

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

## How to use (Dev context)

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
docker run -d -v "./ansible:/home/ansible" -v /var/run/docker.sock:/var/run/docker.sock --name ansible-v1 --env-file=.env ansible-v1
docker exec -it /ansible-v1 /bin/bash -c "ansible-playbook -i ./inventory/staging/hosts.yml site.yml"
```

## How to use CI

### Stable

```bash
# Mode demon de la version stable
docker run -d --name ansible-stable -v "./ansible:/home/ansible" -v /var/run/docker.sock:/var/run/docker.sock --env-file=.env maissacrement/ansibledind:b8c1df7-stable
docker exec -it ansible-stable /bin/bash -c "ansible-playbook -i ./inventory/staging/hosts.yml site.yml"
docker stop ansible-stable
docker rm -f ansible-stable
```

```bash
# Mode run de la version stable
docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock -e "subscription_id=$subscription_id" -e "client_id=$client_id" -e "secret=$secret" -e "tenant=$tenant" docker.io/maissacrement/ansibledind:b8c1df7-stable run ansible-playbook -i ./inventory/staging/hosts.yml site.yml
```

### V1

```bash
# Mode demon de la version V1
docker run -d --name ansible-v1 -v "./ansible:/home/ansible"  -v /var/run/docker.sock:/var/run/docker.sock --env-file=.env maissacrement/ansibledind:b8c1df7-v1
docker exec -it /ansible-v1 /bin/bash -c "ansible-playbook -i ./inventory/staging/hosts.yml site.yml"
docker stop ansible-v1
docker rm -f ansible-v1
```

```bash
# Mode run de la version V1
docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock -e "subscription_id=$subscription_id" -e "client_id=$client_id" -e "secret=$secret" -e "tenant=$tenant" docker.io/maissacrement/ansibledind:b8c1df7-v1 run ansible-playbook -i ./inventory/staging/hosts.yml site.yml
```


### How to use with Vault

In docker container u can now try my vault implementation of generic inventory

```bash
### DEV ONLY ###
export VAULT_PASSWORD="hello"

python3 ~/.ansible_vault_secret/create-vault-local-secret-for-gitlab.py --plain-text-inventory ./inventory/staging/hosts.yml --vault-file test.yml --password hello

export VAULT_HOSTS_SECRETS="$(cat test.yml)"
### END DEV ###

## VAULT_HOSTS_SECRETS and VAULT_PASSWORD need be integrated to the CI

python3 ~/.ansible_vault_secret/generate-inventory.py --list
```

[Voir la documentation complète](./vault_script)

If all is working you can use the dynamics inventory:

```bash
ansible-inventory -i ~/.ansible_vault_secret/generate-inventory.py --list
ansible -m ping -i ~/.ansible_vault_secret/generate-inventory.py all
```

## Next

- Mettre en place une TOOLBOX
