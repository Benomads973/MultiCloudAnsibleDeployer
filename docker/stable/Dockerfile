FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine

RUN mkdir /root/.azure

ENV BUILD_PATH ./docker/stable

COPY ${BUILD_PATH}/requirement.txt /home/requirement.txt

WORKDIR /home

RUN apk update &&\
    apk add --no-cache py3-requests py3-google-auth py3-requests gnupg lsb-release bash curl \
        python3 python3-dev openssl-dev py3-pip cairo-dev gobject-introspection krb5-libs make \
        krb5-dev gobject-introspection-dev cmake build-base gcc g++ gettext curl

RUN curl -LO https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl &&\
    chmod +x ./kubectl &&\
    mv ./kubectl /usr/local/bin/kubectl

ENV VENV_PATH /opt/venv

RUN python -m venv ${VENV_PATH} &&\
    . ${VENV_PATH}/bin/activate &&\
    pip install -r /home/requirement.txt &&\
    pip install "azure-mgmt-recoveryservicesbackup==3.0.0"
    
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Ansible GCP modules
RUN ansible-galaxy collection install azure.azcollection &&\
    ansible-galaxy collection install google.cloud

COPY ${BUILD_PATH}/entrypoint.sh /home/entrypoint.sh

RUN chmod +x /home/entrypoint.sh &&\
    mkdir -p /var/logs &&\
    touch /var/logs/watcher

COPY ${BUILD_PATH}/azure_credentials.ini /root/.azure/credentials
COPY ./ansible /home/ansible

USER root

# TOOLBOX: Établir une hiérarchie permettant à l'utilisateur de créer un ensemble d'outils, afin qu'ils puissent utiliser des scripts déjà fonctionnels de manière plus efficace.
ENV WORKDIR "workdir"
RUN mkdir -p ${WORKDIR}/ansible \
  && mkdir -p ${WORKDIR}/manifest   
WORKDIR ${WORKDIR}

COPY ${BUILD_PATH}/gcloud.sh ./gcloud.sh
RUN chmod 755 gcloud.sh
WORKDIR /home/ansible

RUN echo "export PATH=${PATH}:/usr/local/bin:${VENV_PATH}/bin" >> ~/.bashrc
RUN echo "ansible-playbook -i ./inventory/staging/hosts.yml site.yml" >> ~/.bash_history
ENTRYPOINT ["/home/entrypoint.sh"]