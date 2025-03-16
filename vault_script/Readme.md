# Workflow pour un Inventaire Sécurisé avec Ansible

## Objectif
Ce projet permet de stocker des secrets dans un fichier Vault chiffré et de générer dynamiquement un inventaire Ansible tout en garantissant que les secrets ne sont jamais exposés en clair.

Le processus consiste à créer un fichier Vault contenant des secrets, puis à les déchiffrer dynamiquement dans un pipeline CI/CD pour produire un inventaire sécurisé.

## Préparation
Exportez votre mot de passe ou votre clé de déchiffrement dans une variable d'environnement :

```bash
export VAULT_PASSWORD=hello
```

## 1. Génération d'un fichier de secrets Vault
Le script `create-vault-local-secret-for-gitlab.py` permet de chiffrer un inventaire et de stocker les secrets de manière sécurisée.

### 1.1. Fonctionnalités
- Chargement d'un inventaire YAML
- Chiffrement des variables sensibles
- Génération d'un fichier Vault chiffré

### 1.2. Commandes

#### Génération minimale
```bash
python3 create-vault-local-secret-for-gitlab.py --password $VAULT_PASSWORD
```

#### Génération personnalisée
```bash
python3 create-vault-local-secret-for-gitlab.py \
  --plain-text-inventory inventory.example.yml \
  --vault-file test.yml \
  --password $VAULT_PASSWORD
```

### 1.3. Paramètres
- `--password $VAULT_PASSWORD` : Mot de passe Vault.
- `--plain-text-inventory` : Fichier d'inventaire en clair.
- `--vault-file` : Fichier de sortie chiffré.

### 1.4. Résultat attendu
Un fichier `vault_hosts.yml` contenant des secrets chiffrés avec `ansible-vault`.

```bash
$ANSIBLE_VAULT;1.1;AES256
c73a90b...
```

## 2. Déchiffrement et Génération d'Inventaire
Le script `generate-inventory.py` déchiffre les secrets et génère un inventaire Ansible dynamique.

### 2.1. Prérequis
Installez les dépendances :
```bash
pip install ansible-vault pyyaml python-dotenv
```

### 2.2. Configuration des variables d'environnement
- `VAULT_PASSWORD` : Mot de passe pour déchiffrer les secrets.
- `VAULT_HOSTS_SECRETS` : Contenu chiffré du fichier `vault_hosts.yml`.

Si `VAULT_HOSTS_SECRETS` n'est pas défini, le script utilise `vault_hosts.yml` localement.

### 2.3. Intégration CI/CD
#### Variables d’environnement GitLab CI
```yaml
variables:
  VAULT_HOSTS_SECRETS: |
    $ANSIBLE_VAULT;1.1;AES256
    suite du contenu chiffré
  VAULT_PASSWORD: "mot_de_passe_vault"
```

#### Test de connectivité
```bash
ansible -m ping -i ./generate-inventory.py all
```

### 2.4. Test Local
```bash
export VAULT_PASSWORD="mon_mot_de_passe"
export VAULT_HOSTS_SECRETS="$(cat vault_hosts.yml)"
python3 generate-inventory.py --list
```

#### Sortie attendue
```json
{
  "all": {
    "hosts": ["host1", "host2"],
    "vars": {}
  },
  "_meta": {
    "hostvars": {
      "host1": {...},
      "host2": {...}
    }
  }
}
```

