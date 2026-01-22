# CCCP Explorer

Application web Flask permettant d'explorer et de visualiser des données utilisateur et d'appels depuis un serveur CCCP. L'application fournit une interface web moderne pour consulter les informations récupérées à partir de sources externes.

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Accès Internet (pour installer les dépendances)
- Accès au serveur MySQL (vs-ics-prd-web-fr-505) pour la liste des serveurs
- Accès aux binaires ccenter_report sur le serveur CCCP

## Installation

1. Clonez ou copiez les fichiers du projet sur votre serveur :

```bash
git clone <url_du_projet>
cd <nom_du_projet>
```

ou copiez simplement les fichiers sur votre serveur.

2. Installez les dépendances Python requises :

```bash
pip install -r requirements.txt
```

## Lancement de l'application

Pour démarrer le serveur Web :

```bash
python3 web_server.py
```

Par défaut, le serveur s'exécute sur le port 5000. Vous pouvez accéder à l'application en visitant `http://votre_serveur:5000`.

## Scripts utilitaires

L'application inclut également un script autonome pour récupérer les données :

```bash
python3 get_users_and_calls.py
```

Ce script peut être exécuté indépendamment pour récupérer et traiter les données utilisateur et d'appels. Il supporte les arguments suivants :

- `--host` : Adresse IP du serveur CCCP (défaut : 10.199.30.67)
- `--port` : Port dispatch (défaut : 20103)

## Structure de l'application

### Fichiers principaux

- `web_server.py` - Serveur Flask principal avec toutes les routes API
- `get_users_and_calls.py` - Script pour récupérer les données utilisateur et appels
- `requirements.txt` - Dépendances Python

### Templates HTML

- `templates/index.html` - Page d'accueil par défaut
- `templates/console_minimal.html` - Interface console minimaliste
- `templates/modern_dashboard.html` - Tableau de bord moderne avec visualisation des données

## API Endpoints

### Routes principales

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page principale du dashboard |
| `/console` | GET | Interface console minimaliste |
| `/cst_explorer/<project_name>` | GET | Accès direct à un projet |
| `/api/status` | GET | État actuel du dashboard |
| `/api/users` | GET | Liste des utilisateurs |
| `/api/queues` | GET | Liste des queues |
| `/api/history` | GET | Historique des appels |
| `/api/events` | GET | Événements récents (avec paramètre `limit`) |
| `/api/events/stream` | GET | Stream Server-Sent Events en temps réel |
| `/api/servers` | GET | Liste des serveurs disponibles |
| `/api/select_server` | POST | Sélectionner un serveur |
| `/api/protocol` | GET | Spécification du protocole CCCP |
| `/api/console/session` | POST | Exécuter une commande console pour une session |

### Exemples d'utilisation API

```bash
# Obtenir le statut du dashboard
curl http://localhost:5000/api/status

# Obtenir la liste des utilisateurs
curl http://localhost:5000/api/users

# Obtenir les serveurs disponibles
curl http://localhost:5000/api/servers

# Sélectionner un serveur
curl -X POST http://localhost:5000/api/select_server \
  -H "Content-Type: application/json" \
  -d '{"host": "10.199.30.67", "port": 20103, "project": "mon_projet"}'

# Obtenir les événements (limite de 50)
curl http://localhost:5000/api/events?limit=50
```

## Protocole CCCP

L'application utilise le protocole CCCP pour communiquer avec les serveurs. Les types de messages principaux sont :

- `103` : INITIALIZE
- `10000` : LOGIN
- `10009` : QUERY_LIST
- `20000` : CONNECTION_OK
- `20001` : LOGIN_OK
- `20002` : LOGIN_FAILED
- `20003` : RESULT
- `20007` : LIST_RESPONSE
- `20008` : OBJECT_RESPONSE
- `20009` : SERVER_EVENT

Le format binaire est : `[LENGTH(4)][MESSAGE_ID(4)][PAYLOAD...]`

## Configuration

### Variables de configuration importantes

Dans `web_server.py` :

- `MYSQL_CONFIG` : Configuration de connexion MySQL pour récupérer la liste des serveurs
- `DashboardState` : Classe gérant l'état global du dashboard avec thread d'auto-refresh (30 secondes)

Dans `get_users_and_calls.py` :

- `DEFAULT_IP` : IP par défaut du serveur CCCP (10.199.30.67)
- `DISPATCH_PORT` : Port dispatch par défaut (20103)

## Développement

### Style de code

- **Imports** : Stdlib d'abord, puis third-party (flask, flask_cors), imports explicites
- **Naming** : snake_case pour fonctions/variables, PascalCase pour classes, SCREAMING_SNAKE_CASE pour constantes
- **Types** : Utiliser le module `typing`, dataclasses pour les données structurées, IntEnum pour les énumérations
- **Formatting** : Indentation 4 espaces, limite 120 caractères par ligne, lignes vides entre les définitions de classes
- **Error Handling** : try/except avec exceptions spécifiques, logging via `logger`, inclure le contexte
- **Logging** : `logger = logging.getLogger("cccp")`, utiliser les niveaux INFO/DEBUG/ERROR appropriément
- **Threading** : Utiliser `threading.Lock()` pour l'état partagé, threads daemon pour les tâches de fond
- **Documentation** : Docstrings pour toutes les classes/fonctions publiques, expliquer les paramètres et valeurs de retour

### Linting et formatage

```bash
ruff check . && ruff format .
```

## Dépannage

Si vous rencontrez des problèmes lors de l'installation :

1. Assurez-vous que Python 3.8+ est installé : `python3 --version`
2. Vérifiez que pip est disponible : `pip --version`
3. Essayez d'installer les dépendances dans un environnement virtuel :

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### Problèmes courants

- **Timeout MySQL** : Vérifiez l'accès au serveur vs-ics-prd-web-fr-505
- **Timeout ccenter_report** : Vérifiez l'accès au binaire `/opt/consistent/bin/ccenter_report`
- **Pas de données** : Vérifiez que le serveur CCCP est accessible et que les credentials sont corrects

## Dépendances

Les dépendances spécifiques sont listées dans le fichier `requirements.txt` :

- flask>=2.0.0
- flask-cors>=3.0.0
- mysql-connector-python>=8.0.0

## Licence

Ce projet est développé pour l'exploration et la visualisation des données CCCP.
