#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
from ansible_vault import Vault
from dotenv import load_dotenv

load_dotenv()

def vault_constructor(loader, node):
    """Gestionnaire pour la balise !vault dans YAML."""
    return node.value  # Retourne simplement la valeur brute pour le décryptage ultérieur

# Enregistrer le constructeur pour la balise !vault
yaml.add_constructor('!vault', vault_constructor, Loader=yaml.SafeLoader)

def get_secrets(file_path=None):
    """
    Reads the vault hosts file. 
    If 'file_path' is provided, it prioritizes reading the file from that path.
    Otherwise, it uses the environment variable 'VAULT_HOSTS_FILE' or defaults to 'vault_hosts.yml'.
    """
    # Vérifier si le chemin du fichier est passé en paramètre, sinon vérifier la variable d'environnement
    if os.getenv('VAULT_HOSTS_SECRETS', None) is not None:
        secrets = os.getenv('VAULT_HOSTS_SECRETS').replace('\t', '    ').encode('utf-8', 'ignore')
        return yaml.safe_load(secrets)

    # Si aucun fichier n'est spécifié, utiliser le fichier par défaut
    if not file_path:
        path = os.path.dirname(os.path.realpath(__file__))
        file_path = f"{path}/vault_hosts.yml"

    # Charger le fichier YAML
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            secrets = yaml.safe_load(f)
        return secrets
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier spécifié {file_path} n'a pas été trouvé.")
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur de lecture du fichier YAML {file_path}: {e}")


def decrypt_vault_string():
    """Decrypt vault secrets and format them into an inventory."""
    hosts_data = get_secrets()

    formatted_data = {}
    vault = Vault(os.getenv('VAULT_PASSWORD'))

    for host,secret_value in hosts_data.items():
        host_name = host.split('__')[0].strip()
        secret_key = host.split('__')[1].strip()
        
        if host_name not in formatted_data:
            formatted_data[host_name] = {}

        try:
            formatted_data[host_name][secret_key] = vault.load(secret_value)
        except Exception as e:
            print(f"Error decrypting vault secret for {host_name}::{secret_key}: {e}", file=sys.stderr)
            sys.exit(1)

    # Structurer l'inventaire
    inventory = {
        "all": {
            "hosts": list(formatted_data.keys()),
            "vars": {}
        },
        "_meta": {
            "hostvars": formatted_data
        }
    }

    return inventory

def main():
    """Main entry point for the script."""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        # Générer et afficher l'inventaire en JSON
        inventory = decrypt_vault_string()  # Assurez-vous que 'test' est votre mot de passe de vault
        print(json.dumps(inventory, indent=2))
    else:
        print("Usage: generate-inventory.py --list", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
