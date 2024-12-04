FROM python:3.11.10-alpine3.20

# Set up required directories
RUN mkdir /root/.azure

ENV BUILD_PATH ./docker/v1

# Copy requirements file
COPY ${BUILD_PATH}/requirement.txt /home/requirement.txt

WORKDIR /home

# Install packages in one RUN command to reduce layers and remove unnecessary dependencies after use
RUN apk update && \
    apk add --no-cache \
        py3-requests py3-google-auth py3-requests gnupg lsb-release bash curl python3 python3-dev \
        py3-pip cairo-dev gobject-introspection krb5-libs make krb5-dev gobject-introspection-dev gcc g++ \
        gettext curl && \
    # Install kubectl
    curl -LO https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl && \
    # Clean up unnecessary apk cache to reduce image size
    rm -rf /var/cache/apk/*

# Set up Python virtual environment
ENV VENV_PATH /opt/venv

RUN python -m venv ${VENV_PATH} && \
    . ${VENV_PATH}/bin/activate && \
    pip install --no-cache-dir -r /home/requirement.txt && \
    # Remove unnecessary Python packages after use
    pip uninstall azure-storage azure-storage-blob -y && \
    pip install azure-storage-blob && \
    pip install "azure-cli>=2.51.0" "azure-mgmt-recoveryservicesbackup==3.0.0" && \
    # Clean up pip cache to reduce image size
    rm -rf /root/.cache/pip

# Install Ansible GCP modules
RUN ansible-galaxy collection install google.cloud && \
    # Clean up ansible-galaxy cache
    rm -rf /root/.ansible/collections

# Copy remaining files
COPY ${BUILD_PATH}/init.sh /home/init.sh
COPY ${BUILD_PATH}/azure_credentials.ini /root/.azure/credentials
COPY ./ansible /home/ansible
COPY ${BUILD_PATH}/gcloud.sh /home/gcloud.sh

# Set file permissions and finalize
RUN chmod +x /home/init.sh && \
    chmod 755 /home/gcloud.sh && \
    mkdir -p /var/logs && \
    touch /var/logs/watcher

# Set up working directory and environment
ENV WORKDIR "workdir"
RUN mkdir -p ${WORKDIR}/ansible && \
    mkdir -p ${WORKDIR}/manifest

WORKDIR ${WORKDIR}

# Add environment variables and commands
RUN echo "export PATH=${PATH}:/usr/local/bin:${VENV_PATH}/bin" >> ~/.bashrc && \
    echo "ansible-playbook -i ./inventory/staging/hosts.yml site.yml" >> ~/.bash_history

ENTRYPOINT ["/home/init.sh"]