#!/bin/sh

set -e

# Fonction pour configurer les fichiers avec `envsubst`
substfile () {
    file=$1
    exec 3<$file ; rm $file; envsubst <&3 > $file; exec 3>&-
    echo "file: $file configured"
}

# Fonction principale pour exécuter les configurations
main () {
    # Inject credentials in azure home
    substfile /root/.azure/credentials
    echo "Credentials configured."
}

# Analyse des arguments
case "$1" in
    run)
        main
        shift
        # Si un script ou une commande est spécifié après `run`, l'exécuter
        if [ "$#" -gt 0 ]; then
            exec "$@"
        else
            # Si aucun script ou commande, démarrer un shell interactif
            exec /bin/bash
        fi
        ;;
    daemon|*)
        # Mode par défaut : daemon (garder le conteneur ouvert)
        main
        tail -f /dev/null
        ;;
esac
