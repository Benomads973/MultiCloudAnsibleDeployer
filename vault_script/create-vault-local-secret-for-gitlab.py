from ansible_vault import Vault
import argparse
import yaml
import os
import re

path=os.path.dirname(os.path.realpath(__file__))

def encrypt_and_format_vault(secret, vault_password):
    vault = Vault(vault_password)
    encrypted_secret = vault.dump(secret)

    return encrypted_secret

def get_ciphered_inventory(inventory_file):
    data={}
    with open(f"{inventory_file}", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return data

def generate_local_secret(passwd, inventory_file, secret_dest_file):
    inventory = get_ciphered_inventory(inventory_file)
    with open(f"{secret_dest_file}", "w", encoding="utf-8") as f:
        f.write(''.join(encrypt_and_format_vault(inventory, passwd)))

def parse_arguments():
    """Analyse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Ce programme permet de gérer un inventaire et des secrets de manière locale, en garantissant que ni l'inventaire ni les secrets ne sont poussés sur Git. Il repose sur la récupération sécurisée des secrets stockés dans une variable GitLab. En utilisant cette variable, ainsi qu'un mot de passe pour déchiffrer les données chiffrées dans un vault, le programme est capable de régénérer l'inventaire complet de manière transparente et sécurisée, tout en préservant la confidentialité des informations sensibles.")

    parser.add_argument("--password", type=str, required=True, help="Vault password.")
    parser.add_argument("--inventory", type=str, help="Plain text inventory.")
    parser.add_argument("--output", type=str, help="Output file.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    inventory_file = "inventory.yml"
    if args.inventory:
        if not args.inventory.endswith('.yml'):
            raise "File need be end with .yml"
        inventory_file = args.inventory
    
    secret_dest_file = "vault_hosts.yml"
    if args.output:
        if not args.output.endswith('.yml'):
            raise "File need be end with .yml"
        secret_dest_file = args.output
    
    generate_local_secret(args.password, inventory_file, secret_dest_file)
