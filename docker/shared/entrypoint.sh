#!/bin/sh

set -e

substfile () {
    file=$1
    exec 3<$file ; rm $file; envsubst <&3 > $file; exec 3>&-
    echo "file: $file configured"
}

main () {
    # Inject credentials in azure home
    substfile /root/.azure/credentials # >> $watcher_path
}

main
# keep open docker
tail -f /dev/null
