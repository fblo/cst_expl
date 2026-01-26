# CCCP Explorer - Dashboard Web

## Table des matières
- [Introduction](#introduction)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Variables d'environnement](#variables-denvironnement)
- [API](#api)
- [Dépannage](#dépannage)

## Introduction

CCCP Explorer est une interface web moderne en temps réel qui permet de visualiser les données provenant d'un serveur CCCP (Communication Control and Command Protocol). L'application permet de suivre les utilisateurs actifs, les appels en cours, les files d'attente et les événements en temps réel.

## Fonctionnalités

- Dashboard en temps réel avec données actualisées toutes les 30 secondes
- Thèmes clair et sombre disponibles
- Suivi des utilisateurs connectés avec leur statut et durée de connexion
- Historique des appels et événements
- Visualisation des files d'attente et des agents connectés
- Console de session pour inspecter les détails des sessions spécifiques
- Interface minimaliste pour les opérations de base

## Architecture

Le projet est composé de plusieurs composants :
- `web_server.py` : Application Flask principale
- `get_users_and_calls.py` : Script de récupération des données depuis le serveur CCCP
- `config.py` : Fichier de configuration centralisé
- `ccenter_report` : Binaire exécutable pour communiquer avec le serveur CCCP
- `templates/` : Templates HTML pour l'interface web

## Prérequis

### Système
- Python 3.8 ou supérieur
- MySQL client pour la connexion à la base de données
- Accès à un serveur CCCP avec les ports nécessaires ouverts

### Dépendances Python
- Flask >= 2.0.0
- flask-cors >= 3.0.0
- mysql-connector-python >= 8.0.0

### Dépendances système
- MySQL/MariaDB client libraries
- gcc/g++ pour la compilation éventuelle de modules Python natifs

## Installation

### Méthode 1 : Avec Docker/Podman

```bash
# Construire l'image
podman build -t cccp_dashboard:latest .

# Lancer le conteneur
podman run --rm -p 5000:5000 \
    -e MYSQL_HOST=10.9.8.106 \
    cccp_dashboard:latest
```

### Méthode 2 : Installation locale

1. Cloner le dépôt :
```bash
git clone <url_du_depot>
cd cst_expl
```

2. Installer les dépendances Python :
```bash
pip3 install -r requirements.txt
```

3. Assurez-vous que le binaire `ccenter_report` est exécutable et accessible.

4. Lancer l'application :
```bash
python3 web_server.py
```

## Configuration

### Fichier de configuration

La configuration est centralisée dans `config.py` et peut être personnalisée via des variables d'environnement.

### Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `MYSQL_HOST` | Hôte de la base de données MySQL | `vs-ics-prd-web-fr-505` |
| `MYSQL_USER` | Utilisateur MySQL | `username` |
| `MYSQL_PASSWORD` | Mot de passe MySQL | `passwd` |
| `MYSQL_DATABASE` | Base de données MySQL (optionnelle) | (non définie) |
| `FLASK_HOST` | Interface d'écoute Flask | `0.0.0.0` |
| `FLASK_PORT` | Port d'écoute Flask | `5000` |
| `FLASK_DEBUG` | Mode debug Flask | `false` |
| `LOG_LEVEL` | Niveau de journalisation | `INFO` |

## Utilisation

### Démarrage de l'application

Lancer l'application avec la commande :
```bash
python3 web_server.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

### Navigation

- `/` : Page d'accueil avec sélection des projets
- `/light` : Version thème clair du dashboard
- `/cst_explorer/[nom_du_projet]` : Accès direct à un projet spécifique
- `/cst_explorer_light/[nom_du_projet]` : Version thème clair pour un projet spécifique
- `/console` : Console de session minimaliste
- `/console_light` : Version thème clair de la console
- `/session_console` : Page de console de session dédiée

### Sélection d'un serveur

Pour utiliser le dashboard avec un serveur CCCP spécifique :

1. Accéder à l'API `/api/servers` pour obtenir la liste des serveurs disponibles
2. Utiliser l'API `/api/select_server` avec les paramètres host et port du serveur souhaité
3. Alternativement, utiliser l'URL `/cst_explorer/[nom_du_projet]` pour accéder directement à un projet

## API

L'application expose plusieurs endpoints API :

### Endpoints principaux

- `GET /api/status` : État courant du dashboard
- `GET /api/users` : Liste des utilisateurs
- `GET /api/queues` : Liste des files d'attente
- `GET /api/history` : Historique des appels
- `GET /api/events` : Événements récents
- `GET /api/events/stream` : Flux d'événements en temps réel (Server-Sent Events)
- `GET /api/servers` : Liste des serveurs depuis MySQL
- `POST /api/select_server` : Sélection d'un serveur
- `POST /api/console/session` : Exécution de commandes pour une session spécifique
- `GET /api/protocol` : Spécification du protocole CCCP

### Exemples d'utilisation de l'API

#### Sélection d'un serveur
```bash
curl -X POST http://localhost:5000/api/select_server \
  -H "Content-Type: application/json" \
  -d '{"host": "10.9.30.95", "port": 20263, "project": "MON_PROJET"}'
```

#### Récupération des données en temps réel
```bash
curl http://localhost:5000/api/events/stream
```

## Dépannage

### Problèmes courants

#### Impossible de se connecter à MySQL
- Vérifiez que les variables d'environnement `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` sont correctement définies
- Assurez-vous que le serveur MySQL est accessible depuis votre machine

#### Impossible de se connecter au serveur CCCP
- Vérifiez que l'IP et le port du serveur CCCP sont corrects
- Assurez-vous que les ports nécessaires sont ouverts dans le firewall
- Vérifiez que le binaire `ccenter_report` est correctement installé et fonctionnel

#### Le dashboard ne s'affiche pas
- Vérifiez que l'application est correctement lancée sur le port spécifié
- Vérifiez la console du navigateur pour d'éventuelles erreurs JavaScript
- Vérifiez les logs de l'application Flask

### Journalisation

L'application utilise la journalisation Python avec le niveau spécifié par la variable `LOG_LEVEL`. Les logs sont affichés dans la console de l'application.

### Tests

Pour tester la connexion MySQL :
```bash
python3 -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='vs-ics-prd-web-fr-505',
        user='interactiv',
        password='ics427!'
    )
    print('✅ Connexion MySQL réussie')
    conn.close()
except Exception as e:
    print(f'❌ Erreur MySQL: {e}')
"
```

Pour tester le binaire cccenter_report :
```bash
./ccenter_report --help
```

## Licences et crédits

Le projet utilise les bibliothèques suivantes :
- Flask (BSD License)
- flask-cors (MIT License)
- mysql-connector-python (GPLv2 with FOSS License Exception)

---
*Documentation mise à jour le 26 janvier 2026*