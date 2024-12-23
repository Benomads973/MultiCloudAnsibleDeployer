from ansible_vault import Vault
import argparse
import yaml
import os
import re

path=os.path.dirname(os.path.realpath(__file__))

def encrypt_and_format_vault(secret, vault_password, secret_name):
    vault = Vault(vault_password)
    encrypted_secret = vault.dump(secret)

    # Ajout des tabulations à chaque ligne après le header
    lines = encrypted_secret.splitlines()
    formatted_lines = [lines[0]] + [f"\t{line}" for line in lines[1:]]
    formatted_secret = f"{secret_name}: !vault |\n\t" + "\n".join(formatted_lines)

    return formatted_secret

def get_hosts(inventory_file):
    data={}
    with open(f"{inventory_file}", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return data.get('all', {}).get('hosts', {})

def generate_local_secret(passwd, inventory_file, secret_dest_file):
    hosts = get_hosts(inventory_file)
    mode="w"
    for host, variables in hosts.items():
        # Construire le contenu des secrets pour cet hôte
        #secret_content = "\n".join(f"{key}: {value}" for key, value in variables.items())
        #print(variables)
        result = [ encrypt_and_format_vault(value, passwd, f"{host.replace('-', '_')}__{key}")+"\n" for key, value in variables.items() ]

        # Afficher le résultat
        with open(f"{secret_dest_file}", mode, encoding="utf-8") as f:
            f.write(''.join(result))

        mode="a"

def parse_arguments():
    """Analyse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Ce programme permet de gérer un inventaire et des secrets de manière locale, en garantissant que ni l'inventaire ni les secrets ne sont poussés sur Git. Il repose sur la récupération sécurisée des secrets stockés dans une variable GitLab. En utilisant cette variable, ainsi qu'un mot de passe pour déchiffrer les données chiffrées dans un vault, le programme est capable de régénérer l'inventaire complet de manière transparente et sécurisée, tout en préservant la confidentialité des informations sensibles.")

    parser.add_argument("--password", type=str, required=True, help="Vault password.")
    parser.add_argument("--plain-text-inventory", type=str, help="Vault password.")
    parser.add_argument("--vault-file", type=str, help="Vault password.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    inventory_file = "inventory.yml"
    if args.plain_text_inventory:
        if not args.plain_text_inventory.endswith('.yml'):
            raise "File need be end with .yml"
        inventory_file = args.plain_text_inventory
    
    secret_dest_file = "vault_hosts.yml"
    if args.vault_file:
        if not args.vault_file.endswith('.yml'):
            raise "File need be end with .yml"
        secret_dest_file = args.vault_file
    
    generate_local_secret(args.password, inventory_file, secret_dest_file)
