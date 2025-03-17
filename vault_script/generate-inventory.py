#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
from ansible_vault import Vault
from dotenv import load_dotenv
from ansible.parsing.vault import VaultLib, AnsibleVaultError
from ansible.errors import AnsibleError
import base64

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
        secrets = os.getenv('VAULT_HOSTS_SECRETS', '')
        return base64.b64decode(secrets)

    # Si aucun fichier n'est spécifié, utiliser le fichier par défaut
    if not file_path:
        path = os.path.dirname(os.path.realpath(__file__))
        file_path = f"{path}/vault_hosts.yml"

    # Charger le fichier YAML
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            secrets = f.read() # yaml.safe_load(f) print(secrets)
            secrets = base64.b64decode(secrets)
        return secrets
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier spécifié {file_path} n'a pas été trouvé.")
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur de lecture du fichier YAML {file_path}: {e}")


import logging

def decrypt_vault_string():
    """Decrypt vault secrets and format them into a dynamic Ansible inventory."""
    
    try:
        secret_value = get_secrets()
        if not secret_value:
            logging.error("Les secrets sont vides ou introuvables.")
            return None
        
        vault_password = os.getenv('VAULT_PASSWORD', '')
        if not vault_password:
            logging.error("La variable d'environnement 'VAULT_PASSWORD' est absente.")
            return None

        vault = Vault(vault_password)
        decrypted_content = vault.load(secret_value)

        # Vérification de la structure attendue
        if not isinstance(decrypted_content, dict):
            logging.error("Le contenu déchiffré n'est pas un dictionnaire valide.")
            return None
        
        inventory = {"_meta": {"hostvars": {}}}

        for group, data in decrypted_content.items():
            if not isinstance(data, dict) or "hosts" not in data:
                logging.warning(f"Le groupe {group} ne contient pas de section 'hosts'. Il sera ignoré.")
                continue

            # Ajout des hôtes et de leurs variables
            inventory[group] = {
                "hosts": list(data["hosts"].keys()),
                "vars": data.get("vars", {})
            }

            # Ajout des hostvars au niveau global
            inventory["_meta"]["hostvars"].update(data["hosts"])

    except AnsibleError as e:
        logging.error(f"Erreur Ansible : {e}")
        return None
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
        return None

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
