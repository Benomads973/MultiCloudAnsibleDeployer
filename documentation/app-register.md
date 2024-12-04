# Enregistrer une application sur Azure pour vos déploiements d’infrastructure as code

Introduction
Il est recommandé d'enregistrer une application sur Azure pour vos déploiements d'infrastructure as code. Cela permet d'utiliser des identifiants sécurisés et automatisés, offrant ainsi une gestion des accès plus flexible et sécurisée par rapport à l'utilisation d'un compte utilisateur avec mot de passe.

## Méthode
Dans la barre de recherche Azure, tapez : Microsoft Entra ID.
Ensuite, cliquez sur "Gérer", puis sur "Inscription d'application".
                                                                                                            <img src="../assets/inscription.png">                                                                    

Sous Sup de Vinci | Inscription d'application, vous verrez "Nouvelle application".
Donnez-lui un nom, par exemple IAC_DEPLOYER, et conservez les mêmes paramètres.
 
<img src="../assets/newapp.png">
            
Vous accéderez à votre application avec ses informations.

<img src="../assets/appclientid.png">
 
Vous venez de récupérer le « client_id », qui n’est autre que l’<username> de votre application.

Les secrets
Toujours dans votre application, à gauche, vous devrez chercher l’onglet "Gérer", puis sélectionner "Certificats & Secrets".

<img src="../assets/appsecret.png">
 
Vous devrez générer un nouveau secret et extraire la clé dans le champ "valeur" du tableau.

Prérequis avant de vous connecter à votre application
Connectez-vous en tant qu’utilisateur, peu importe où vous le faites (en local ou sur Azure CLI), et reliez votre abonnement à votre application :
az login --username <user> --password <pass> 
az ad sp create-for-rbac --name <name_app> --role Owner –scopes /subscriptions/<subscription_id>

Connection en tant qu’application :
 az login --service-principal --username <app_id> --password <app_secret> --tenant <tenant>

Comme je vous l'ai dit, tous les droits sont gérés par votre abonnement, donc par exemple avec 'Azure for Students' :

<img src="../assets/subscription.png">
  
Si vous allez sur IAM et que vous sélectionnez « Ajouter une attribution de rôle » 

<img src="../assets/IAM.png">
 
Pour l'exemple, je vais sélectionner un rôle avec le plus de privilèges dans « Rôles d’administrateur privilégié » :

<img src="../assets/IAM_ROLES.png">

Quand vous cliquez sur « Suivant », dans « Membres », vous sélectionnez « Sélectionner des membres » et vous choisissez votre application :

<img src="../assets/IAM_ADD_ROLES.png">

Le rôle souhaité est donc ajouté à votre application, qui dispose des droits dans le périmètre des rôles que vous lui avez attribués. Ces rôles peuvent être multiples.

<img src="../assets/IAM_APPLY_ROLES.png">