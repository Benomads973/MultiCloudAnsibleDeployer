FROM python:3.11.10-alpine3.20

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

# Image minimale
FROM python:3.11-alpine

ENV VENV_PATH /opt/venv
ENV SHARED_PATH ./docker/shared

COPY --from=0 ${VENV_PATH} ${VENV_PATH}
COPY --from=0 /usr/local/bin/kubectl /usr/local/bin/kubectl
COPY --from=0 /root/.ansible /root/.ansible

# Copy remaining files
COPY ${SHARED_PATH}/entrypoint.sh /home/entrypoint.sh
COPY ${SHARED_PATH}/azure_credentials.ini /root/.azure/credentials
COPY ./ansible /home/ansible
COPY ${SHARED_PATH}/gcloud.sh /home/gcloud.sh

# Set file permissions and finalize
RUN chmod +x /home/entrypoint.sh && \
    chmod 755 /home/gcloud.sh

RUN apk update && \
    apk add --no-cache gettext bash

WORKDIR /home/ansible

# Add environment variables and commands
RUN echo "export PATH=${PATH}:/usr/local/bin:${VENV_PATH}/bin" >> ~/.bashrc && \
    echo "ansible-playbook -i ./inventory/staging/hosts.yml site.yml" >> ~/.bash_history

ENTRYPOINT ["/home/entrypoint.sh"]
