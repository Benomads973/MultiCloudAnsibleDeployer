#!/bin/sh

set -e

substfile () {
    file=$1
    exec 3<$file ; rm $file; envsubst <&3 > $file; exec 3>&-
    echo "file: $file configured"
}

printer () {
    ansible-playbook /home/deploy.yml
    kubectl get pods
    kubectl get nodes
    kubectl get services
    #echo -e """\nMachine is ready now !!!""" >> $watcher_path
}

timetosay () {
    sleep 1 && $1
}

main () {
    watcher_path=/var/logs/watcher
    substfile /root/.azure/credentials >> $watcher_path
    timetosay printer &
    tail -f $watcher_path
    
}

main