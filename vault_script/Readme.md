# Workflow pour générer et utiliser un inventaire sécurisé avec Ansible

Objectif

Ce projet permet de sécuriser vos secrets dans un fichier Vault chiffré et de les utiliser pour générer dynamiquement un fichier d'inventaire pour Ansible, tout en garantissant que les secrets ne sont jamais exposés en clair dans votre système de contrôle de version (Git).

Le processus commence par la génération d'un fichier Vault localement, où les secrets sont sécurisés. Ensuite, ces secrets peuvent être utilisés dans un pipeline CI/CD pour déchiffrer et générer un inventaire de manière dynamique sans compromettre la sécurité des données sensibles.

Préparation : Exportez votre mot de passe ou votre clé de déchiffrement dans une variable d'environnement :

```bash
export VAULT_PASSWORD=hello
```

## Étape 1 : Générer un fichier de secrets Vault

Le script create-vault-local-secret-for-gitlab.py vous permet de générer un fichier Vault chiffré à partir d'un fichier d'inventaire en texte brut. Le fichier Vault pourra ensuite être utilisé pour sécuriser les informations sensibles en les extrayant et en les définissant comme variables d'environnement locales.
Ces variables pourront ensuite être ajoutées manuellement à l'environnement GitLab. Ce processus permet de préparer les secrets pour être déchiffrés dynamiquement dans un pipeline CI/CD en utilisant un mot de passe Vault.

### Étape 1.1. Fonctionnalité

Le script utilise la bibliothèque ansible-vault pour chiffrer les secrets. Il permet de :

- Charger un inventaire d'hôtes à partir d'un fichier YAML (ex : inventory.yml).
- Chiffrer les variables sensibles associées à chaque hôte (par exemple, des mots de passe ou des clés API).
- Générer un fichier de secrets chiffrés à utiliser localement pour définir les variables d'environnement dans GitLab. Ensuite, le second script (non mentionné ici) pourra être utilisé pour déchiffrer le Vault dans le pipeline CI/CD et générer dynamiquement un inventaire sécurisé.

### Étape 1.2. Commandes:

Génération minimale avec les fichiers par défaut inventory.yml et vault_hosts.yml :

Si vous avez un fichier d'inventaire inventory.yml par défaut et que vous souhaitez générer un fichier vault_hosts.yml avec des secrets chiffrés :

```bash
python3 create-vault-local-secret-for-gitlab.py --password $VAULT_PASSWORD
```

Génération personnalisée à partir d'un inventaire en texte brut :

Si vous avez un fichier d'inventaire spécifique (ex. inventory.example.yml) et souhaitez personnaliser le nom du fichier de sortie (ex. test.yml), vous pouvez utiliser cette commande :

```bash
python3 create-vault-local-secret-for-gitlab.py \
  --plain-text-inventory inventory.example.yml \
  --vault-file test.yml \
  --password $VAULT_PASSWORD
```

### Étape 1.3. Paramètres:

```bash
--password $VAULT_PASSWORD : Mot de passe Vault utilisé pour chiffrer les secrets. Il doit être fourni soit en ligne de commande, soit via une variable d'environnement (ex. VAULT_PASSWORD).

--plain-text-inventory inventory.example.yml : Chemin vers le fichier d'inventaire en texte clair, qui contient les hôtes et les variables sensibles (par exemple, des clés API ou des mots de passe).

--vault-file test.yml : Chemin du fichier de sortie où seront enregistrés les secrets chiffrés. Le format .yml est requis.
```

### Étape 1.4. Résultat attendu:

Un fichier vault_hosts.yml ou le fichier spécifié sera généré, contenant des secrets chiffrés. Ce fichier pourra être utilisé pour sécuriser vos informations sensibles localement en générant des variables d'environnement. Ces variables pourront être ajoutées manuellement dans votre pipeline CI/CD pour être utilisées dans des tâches de déchiffrement et de génération d'inventaire dynamiquement.

Exemple de contenu du fichier généré :

```bash
host1__api_key: !vault |
    $ANSIBLE_VAULT;1.1;AES256
        f7a862f...
host1__db_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
        c73a90b...
host2__api_key: !vault |
    $ANSIBLE_VAULT;1.1;AES256
        d81a9f3...
```

Chaque secret est préfixé par le nom de l'hôte et la clé correspondante, suivis du chiffrement Vault.

### Étape 1.5. Sécurité et Meilleures Pratiques

1. Ne jamais exposer le mot de passe Vault en clair : Le mot de passe Vault doit être géré de manière sécurisée. Utilisez des variables d'environnement dans les pipelines CI/CD pour éviter qu'il n'apparaisse en clair dans les logs ou le code source.

2. Utilisation du fichier Vault dans CI/CD : En production, injectez le fichier chiffré (vault_hosts.yml) dans les environnements CI/CD et récupérez les secrets en utilisant la commande ansible-vault ou un outil équivalent pour déchiffrer les données au moment de l'exécution, et générer dynamiquement un inventaire sécurisé dans votre pipeline.

3. Ne jamais stocker de secrets en clair : Le but principal de ce processus est de vous assurer que vos secrets ne sont jamais exposés en clair dans les dépôts Git ou dans les fichiers de configuration.

4. Chiffrement individuel des variables sensibles : Le chiffrement est effectué au niveau de chaque variable sensible, ce qui permet de gérer de manière granulaire les informations sensibles pour chaque hôte.

## Étape 2 : Déchiffrer et générer un inventaire dynamique

Ce guide explique comment utiliser generate-inventory.py pour déchiffrer les secrets d'un fichier Vault et produire un inventaire dynamique sécurisé, tout en mettant en avant les bonnes pratiques pour éviter de compromettre les secrets (notamment dans un contexte CI/CD).

### Étape 2.1 : Préparation

Prérequis :

- Python 3 installé.
- Les bibliothèques nécessaires : ansible-vault, pyyaml, python-dotenv. Installez-les avec :
```bash
pip install ansible-vault pyyaml python-dotenv
```
- Fichiers requis :
    - Localement : Un fichier Vault nommé vault_hosts.yml contenant les secrets chiffrés.
    - CI/CD : Secrets directement dans une variable d'environnement (VAULT_HOSTS_SECRETS)

### Etape 2.2 Configuration des variables d'environnement


1. VAULT_PASSWORD : Contient le mot de passe pour déchiffrer les secrets.
2. VAULT_HOSTS_SECRETS : 
    - Alternative au fichier vault_hosts.yml.
    - Recommandée dans les pipelines CI/CD pour éviter tout stockage local des secrets.

Astuce : Si VAULT_HOSTS_SECRETS n’est pas défini, le script recherche automatiquement le fichier vault_hosts.yml dans le répertoire de generate-inventory.py.

### 2.3 Production et CI/CD

Dans un contexte de production ou de CI/CD, le fichier vault_hosts.yml ne doit jamais être présent localement ou dans le dépôt Git. Les secrets doivent être gérés uniquement via des variables d’environnement sécurisées.


### Etape 2.3.1: Créez deux variables d’environnement dans la CI/CD

```
VAULT_PASSWORD : Contient le mot de passe pour déchiffrer les secrets.
VAULT_HOSTS_SECRETS : Contient directement le contenu chiffré de vault_hosts.yml
```

Exemple de configuration dans un pipeline GitLab CI :

```bash
variables:
  VAULT_HOSTS_SECRETS: |
    node_master__ansible_port: !vault |
        $ANSIBLE_VAULT;1.1;AES256
        suite du contenu chiffré de vault_hosts.yml pour la variable 'ansible_port'
    node_master__ansible_user: !vault |
        $ANSIBLE_VAULT;1.1;AES256
        suite du contenu chiffré de vault_hosts.yml pour la variable 'ansible_user'
    suite du contenu chiffré de vault_hosts.yml ...
  VAULT_PASSWORD: "mot_de_passe_vault"
```

Testez la connectivité des hôtes avec Ansible :

```bash
# Test de la connectivité des hôtes avec Ansible, en utilisant l'inventaire généré
ansible -m ping -i ./generate-inventory.py all
```

### 2.3.2 Test local

Pour valider le fonctionnement du déchiffrement avant intégration en CI/CD, vous pouvez utiliser un fichier Vault temporaire (localement uniquement). Ce fichier ne doit jamais être poussé dans le dépôt.

Étapes pour un test local :

1. Placez temporairement votre fichier vault_hosts.yml dans le même répertoire que generate-inventory.py.
2. Exécutez les commandes suivantes :

```bash
# Ne jamais exposer le fichier vault_hosts.yml dans les dépôts Git ou dans des environnements non sécurisés
# Pour tester localement, placez le fichier vault_hosts.yml dans le même répertoire
# Assurez-vous que VAULT_PASSWORD et VAULT_HOSTS_SECRETS sont configurés avant d'exécuter la commande
# VAULT_HOSTS_SECRETS est défini à partir du contenu de vault_hosts.yml
export VAULT_PASSWORD="mon_mot_de_passe"
export VAULT_HOSTS_SECRETS="$(cat vault_hosts.yml)" # (Uniquement pour les tests locaux)
python3 generate-inventory.py --list  # Vérification de l'inventaire généré.
```

Exemple de sortie attendue (python3 generate-inventory.py --list):
```json
{
  "all": {
    "hosts": ["host1", "host2"],
    "vars": {}
  },
  "_meta": {
    "hostvars": {
      "host1": {
        "api_key": "clé déchiffrée",
        "db_password": "mot de passe déchiffré"
      },
      "host2": {
        "api_key": "clé déchiffrée"
      }
    }
  }
}
```

Une fois testé, supprimez immédiatement le fichier local pour éviter tout risque de fuite. Par securité le fichier du secret généré sont sur notre .gitignore

### 2.3.3 Rappel de sécurité

```
- Ne jamais stocker vault_hosts.yml dans le dépôt Git ou sur une machine partagée.
- Utilisez toujours VAULT_HOSTS_SECRETS en CI/CD pour encapsuler vos secrets dans des variables d’environnement.
- Gérez les permissions des secrets avec soin et limitez leur accès aux utilisateurs ou pipelines nécessaires.
```

### Étape 3 : Utilisation avec Ansible

Testez la connectivité des hôtes définis dans l'inventaire :

```bash
# Test de la connectivité des hôtes avec Ansible, en utilisant l'inventaire généré
ansible -m ping -i ./generate-inventory.py all

Explications :
-m ping : Module Ansible pour tester la connectivité.
-i ./generate-inventory.py : Utilisation de l’inventaire dynamique généré par le script.
```

Bonnes pratiques
- Exécutez votre pipeline en s’assurant que le fichier Vault n’est jamais présent sur la machine ou dans les logs.
- Ne jamais pousser de secrets dans le dépôt Git.
- Generer en local vos secret
- Restreignez a certains utilisateur la mise a jour des variables environnement