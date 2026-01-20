# CCCP Explorer

CCCP Explorer est une application web Flask qui permet d'explorer et de visualiser des données utilisateur et d'appels. L'application fournit une interface web moderne pour consulter les informations récupérées à partir de sources externes.

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Accès Internet (pour installer les dépendances)

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

Ce script peut être exécuté indépendamment pour récupérer et traiter les données utilisateur et d'appels.

## Structure des fichiers

- `web_server.py` - Serveur Flask principal
- `get_users_and_calls.py` - Script pour récupérer les données
- `requirements.txt` - Dépendances Python
- `templates/` - Modèles HTML pour l'interface Web
 - `index.html` - Page d'accueil
  - `console_minimal.html` - Interface console minimaliste
  - `modern_dashboard.html` - Tableau de bord moderne
- `AGENTS.md` - Documentation technique et lignes directrices de développement

## Configuration

Aucune configuration supplémentaire n'est requise pour un déploiement de base. L'application utilisera les paramètres par défaut.

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

## Dépendances

Les dépendances spécifiques sont listées dans le fichier `requirements.txt`. Elles comprennent notamment Flask et Flask-CORS pour le développement Web.
