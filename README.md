## Multi-Cloud Deployment with Ansible

This project aims to provide a unified, flexible environment to deploy Kubernetes projects on multiple clouds (Azure, GCP, and custom host machines) using Ansible. The key feature of this solution is the use of a dynamic inventory, allowing seamless deployment on any infrastructure, regardless of the cloud provider. This containerized solution supports different environments with ease, addressing compatibility issues, especially with Azure.

## ENVIRONMENT SETUP

Docker Image
We use a custom Docker image that supports Ansible deployments across Azure, GCP, and other host machines.

```yaml
image: docker.io/maissacrement/ansibledind:10e77ca-stable
```
You can download the image from [Dockerhub](https://hub.docker.com/repository/docker/maissacrement/ansibledind/general)

## DOCKER API Setup and Requirements

For setting up Docker, follow the installation and post-installation steps:

[Install Docker](https://docs.docker.com/engine/install/)

[Post-installation steps for Docker](https://docs.docker.com/engine/install/linux-postinstall)

## CONFIGURATION: .env file or variables

There are two modes for connection: Student Mode (via email and password) and Subscription Mode (via application credentials). You can choose based on your needs.

### 1. Student Mode:

Provide Azure login credentials:

```bash
email: <azure login email> 
password: <azure login password>
```

### 2. Subscription Mode (Azure):

This mode uses the Azure service principal to authenticate via client credentials. These details can be retrieved from the Azure portal.

### 2.1: Get account credentials

Run `az account show` in Azure Cloud Shell to fetch your subscription and tenant IDs, the prompter will display a JSON with `subscription_id` and `tenant`

```yaml
subscription_id: <'id' field>
tenant: <'tenantId' field>
```

### 2.2: Register an application in Azure and get the client ID and secret.

1. Select "App registration || Inscriptions d'applications"

2. Create a new application on "Register application || Inscrire une application" or use an existing Application

3. Select or enter in an Application on "overview || vue d'ensemble", in the left menu you will see a "Bases" tab

```yaml
client_id: <'Application (client) ID || ID d'application (client)' field> 
```

4. Click on "Certificats & secrets" and create a new secret with "New client secret || Nouveau secret client" from "Secret ID || ID de secret"

```yaml
secret: <'value || valeur' field> # Get secret value
```

### Env with Vault (From the container)

This Python script directly generates a dynamic inventory based on environment variables or a specific file, which ensures that no sensitive data is left in the repository. You can store all types of secrets, such as those used by the Azure CLI. It was specifically created for cloud and on-premise hosts.

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

If all is working, you can use the dynamic inventory:

```bash
ansible-inventory -i ~/.ansible_vault_secret/generate-inventory.py --list
ansible -m ping -i ~/.ansible_vault_secret/generate-inventory.py all
```

## USING THE PROJECT

Building and Running the Docker Image

### 1. Build and Run Stable Version

### 1.1 Build and run the Docker image:

There are two versions of the Docker image to choose from: stable and v1.

```bash
# Build stable image
make build-stable  # Builds the Docker image (Local name: /ansibledind-stable)
make dev-stable    # Run the image in the background and attach bash session

# Or build and run version 1 call v1 == make build-v1
make build  # Builds the Docker image (Local name: /ansibledind)
make dev    # Run the image in the background and attach bash session
```

### Manual Launch:

You can also build and run the Docker container manually:

```bash
# depuis le repertoire courrant
docker build -t ansible-v1 . -f ./docker/V1/Dockerfile
docker run -d -v "./ansible:/home/ansible" -v /var/run/docker.sock:/var/run/docker.sock --name ansible-v1 --env-file=.env ansible-v1
docker exec -it /ansible-v1 /bin/bash -c "ansible-playbook -i ./inventory/staging/hosts.yml site.yml"
```

## Workflow

The CI/CD workflow for Azure uses environment variables in Docker to execute deployments on Azure. This process is designed for a multi-cloud environment, with a focus on Azure. The Azure credentials are injected as plaintext variables into the Docker environment to allow Azure connectivity for Kubernetes deployments.

### Ansible Stable image

The daemon mode allows running the daemon in the background while performing actions and saving the initial state of the machine.

```bash
# Mode demon de la version stable
docker run -d --name ansible-stable -v "./ansible:/home/ansible" -v /var/run/docker.sock:/var/run/docker.sock --env-file=.env maissacrement/ansibledind:b8c1df7-stable
docker exec -it ansible-stable /bin/bash -c "ansible-playbook -i ./inventory/staging/hosts.yml site.yml"
docker stop ansible-stable
docker rm -f ansible-stable
```

The run mode is interactive and used for direct execution without a script, eliminating the need for passing previous actions.

```bash
# Mode run de la version stable
docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock -e "subscription_id=$subscription_id" -e "client_id=$client_id" -e "secret=$secret" -e "tenant=$tenant" docker.io/maissacrement/ansibledind:b8c1df7-stable run ansible-playbook -i ./inventory/staging/hosts.yml site.yml
```

### Ansible V1 image

The same setup applies for our V1 image.

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

## USING IN CI/CD

GitHub: Example of using our dynamic vault inventory script in a local decryption context. It's recommended to use environment variables.

```yaml
vault-is-working:
  name: Ansible Vault generic inventory
  runs-on: ubuntu-latest
  container:
    image: maissacrement/ansibledind:10e77ca-stable
    options: --entrypoint="/home/entrypoint.sh run" --privileged -u root
  steps:
    - name: Checkout Code
      uses: actions/checkout@v3  
    - name: Run Vault execution
      run: |
        #### Need be execute locally ####
        export VAULT_PASSWORD="hello" # Need be stored GitHub environment secrets
        python3 /root/.ansible_vault_secret/create-vault-local-secret-for-gitlab.py --plain-text-inventory ./ansible/inventory/staging/hosts.yml --vault-file test.yml --password hello # Generate locally inventory secret
        #### Done local execution ####
        export VAULT_HOSTS_SECRETS="$(cat test.yml)" # Get the inventory secret generated locally and store it in the GitHub environment secrets
        echo "================= generate inventory ================="
        python3 /root/.ansible_vault_secret/generate-inventory.py --list
        echo "================= original inventory ================="
        cat ./ansible/inventory/staging/hosts.yml  
        echo "================= veryfy inventory ================="
        ansible-inventory -i /root/.ansible_vault_secret/generate-inventory.py --list  
        echo "================= ping inventory ================="
        ansible -m ping -i /root/.ansible_vault_secret/generate-inventory.py all
```

GitLab: Example of using our dynamic vault inventory script in a local decryption context. Again, using environment variables is recommended.

```yaml
image: 
  name: maissacrement/ansibledind:10e77ca-stable
  entrypoint: ["/home/entrypoint.sh", "run"]

...

vault-is-working:
  stage: deploy
  script:
    - echo "Building the project ${MY_SSH_PASS:-none}"
    - #### Need be execute locally ####
    - export VAULT_PASSWORD="hello" # Need be stored GitHub environment secrets
    - python3 /root/.ansible_vault_secret/create-vault-local-secret-for-gitlab.py --plain-text-inventory ./ansible/inventory/staging/hosts.yml --vault-file test.yml --password hello
    - #### Done local execution ####
    - export VAULT_HOSTS_SECRETS="$(cat test.yml)" # Get the inventory secret generated locally and store it in the GitHub environment secrets
    - echo "================= generate inventory ================="
    - python3 /root/.ansible_vault_secret/generate-inventory.py --list
    - echo "================= original inventory ================="
    - cat ./ansible/inventory/staging/hosts.yml  
    - echo "================= veryfy inventory ================="
    - ansible-inventory -i /root/.ansible_vault_secret/generate-inventory.py --list  
    - echo "================= ping inventory ================="
    - ansible -m ping -i /root/.ansible_vault_secret/generate-inventory.py all
```

## Next

- Mettre en place une TOOLBOX
