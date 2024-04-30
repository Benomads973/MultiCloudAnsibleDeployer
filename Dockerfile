FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine

RUN mkdir /root/.azure

COPY ./requirement.txt /home/requirement.txt

WORKDIR /home

RUN apk update &&\
    apk add --no-cache py3-requests py3-google-auth py3-requests gnupg lsb-release bash curl python3 python3-dev py3-pip cairo-dev gobject-introspection krb5-libs make krb5-dev gobject-introspection-dev gcc g++ gettext curl

RUN curl -LO https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl &&\
    chmod +x ./kubectl &&\
    mv ./kubectl /usr/local/bin/kubectl

ENV VENV_PATH /opt/venv

RUN python -m venv ${VENV_PATH} &&\
    . ${VENV_PATH}/bin/activate
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -r /home/requirement.txt &&\
    pip uninstall azure-storage -y &&\
    pip uninstall azure-storage-blob -y &&\
    pip install azure-storage-blob &&\
    pip install "azure-cli>=2.51.0" &&\
    pip install "azure-mgmt-recoveryservicesbackup==3.0.0"

# Install Ansible GCP modules
RUN ansible-galaxy collection install google.cloud

COPY ./init.sh /home/init.sh

RUN chmod +x /home/init.sh &&\
    mkdir -p /var/logs &&\
    touch /var/logs/watcher

COPY ./azure_credentials.ini /root/.azure/credentials
COPY ./deploy_cli.yml /home/deploy_cli.yml
COPY ./deploy.yml /home/deploy.yml
COPY ./kubeapplication.yml /home/kubeapplication.yml

USER root

# TOOLBOX: Établir une hiérarchie permettant à l'utilisateur de créer un ensemble d'outils, afin qu'ils puissent utiliser des scripts déjà fonctionnels de manière plus efficace.
ENV WORKDIR="/workdir"
RUN mkdir -p ${WORKDIR}/ansible \
  && mkdir -p ${WORKDIR}/manifest   
WORKDIR ${WORKDIR}

COPY startup.sh .
RUN chmod 755 startup.sh
WORKDIR /home

RUN echo "export PATH=${PATH}:/usr/local/bin:${VENV_PATH}/bin" > ~/.bashrc
ENTRYPOINT ["/home/init.sh"]