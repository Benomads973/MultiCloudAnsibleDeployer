FROM docker:24.0.5-cli

RUN mkdir /root/.azure

COPY ./requirement.txt /home/requirement.txt

WORKDIR /home


RUN apk update &&\
    apk add bash curl python3 python3-dev py3-pip cairo-dev gobject-introspection krb5-libs make krb5-dev gobject-introspection-dev gcc g++

RUN curl -LO https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl &&\
    chmod +x ./kubectl &&\
    mv ./kubectl /usr/local/bin/kubectl

RUN pip install -r /home/requirement.txt &&\
    pip uninstall azure-storage -y &&\
    pip uninstall azure-storage-blob -y &&\
    pip install azure-storage-blob &&\
    pip install "azure-cli>=2.51.0" &&\
    pip install "azure-mgmt-recoveryservicesbackup==3.0.0"

COPY ./init.sh /home/init.sh

RUN chmod +x /home/init.sh &&\
    mkdir -p /var/logs &&\
    touch /var/logs/watcher

COPY ./azure_credentials.ini /root/.azure/credentials
COPY ./deploy_cli.yml /home/deploy_cli.yml
COPY ./deploy.yml /home/deploy.yml
COPY ./kubeapplication.yml /home/kubeapplication.yml

USER root
RUN echo "export PATH=${PATH}:/usr/local/bin" > ~/.bashrc
ENTRYPOINT ["/home/init.sh"]