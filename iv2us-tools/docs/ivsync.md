# Documentation du script iv-sync

## Description
Le script iv-sync est utilisé afin de synchroniser les données de configuration d'un projet présent sur un webadmin vers le serveur d'API.

## Compatibilité
Cette version d'iv-sync est comptatible avec la __version 10__ de configAPI.

## Usage
iv-sync est fourni par le dépot __iv2us-tools__.
Voici les options accessibles:
```
-h/--help: décrit l'usage d'iv-sync
-q/--quiet: applique les changements sans confirmation.
--apionly: ne pas migrer les objets de scénarios.
```
```
--calendarsapi: fait la migration des dossiers des jours spéciaux, ne doit être fait qu'une seule fois.
--specialdays: fait la migration des jours speciaux vers leur calendriers, ne doit être fait qu'une seule fois.
```
```
-w/--whitelabel: définit la marque blanche.
-p/--project: définit le projet.
```

```
--api-host: nom de l'hôte ou adresse du serveur d'API. Si non utilisé, valeur par défaut: vs-ics-prd-iap-fr-901-50
--api-port: port sur lequel le serveur d'API écoute.
--api-no-ssl: désactive SSL, utile si port != 443.
-k/--api-key: clef d'API Overlord (ConfigAPI)
```

```
--portal-host: nom de l'hôte ou adresse du portail pour les webadmins. Si non utilisé, valeur par défaut: vs-ics-prd-web-fr-505
--portal-db: nom de la base de données sur le portail, par défaut: interactivportal.
--portal-user: utilisateur de la base de données sur le portail, par défaut: interactiv.
--portal-password: mot de passe de l'utilisateur sur le portail.
```

```
--webadmin-host: nom de l'hote ou adresse du webadmin sur lequel se trouve le/les projet(s) à migrer.
--webadmin-db: base de donnée du webadmin.
--webadmin-user: utilisateur de la base de données sur le webadmin, par défaut: interactiv.
--webadmin-password: mot de passe de l'utilisateur sur le webadmin.
```

## Notes
- Si aucune marque blanche n'est spécifiée, toutes les marques blanches et tous les projets seront traités.
- Si aucun projet n'est spécifié, tous les projets de la marque blanche seront traités.
- Il est important de faire un iv-sync sur un serveur d'API à jour. Chaque version du script correspond à une version de configAPI précise.