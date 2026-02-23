# AGENTS.md - Guide de Développement CCCP Explorer

Ce fichier fournit des directives pour les agents IA travaillant sur le code source de CCCP Explorer.

## Présentation du Projet

CCCP Explorer est un dashboard web basé sur Flask qui se connecte aux serveurs CCCP et affiche des données en temps réel (utilisateurs, appels, files d'attente, événements). Le code source comprend :
- `web_server.py` - Application Flask principale
- `get_users_and_calls.py` - Module de récupération des données du protocole CCCP
- `config.py` - Configuration centralisée
- `templates/` - Modèles HTML pour l'interface utilisateur

## Commandes de Build et d'Exécution

### Développement
```bash
# Installer les dépendances
pip3 install -r requirements.txt

# Vérifier la syntaxe Python (lint de base)
python3 -m py_compile web_server.py
python3 -m py_compile get_users_and_calls.py
python3 -m py_compile config.py

# Vérification de types (optionnel, nécessite mypy)
pip3 install mypy && mypy web_server.py get_users_and_calls.py config.py

# Lancer l'application
python3 web_server.py

# Lancer avec configuration personnalisée via variables d'environnement
MYSQL_HOST=10.9.8.106 FLASK_DEBUG=true python3 web_server.py
```

### Docker/Podman
```bash
# Construire l'image
podman build -t cccp_dashboard:latest .

# Lancer le conteneur
podman run --rm -p 5000:5000 \
    -e MYSQL_HOST=10.9.8.106 \
    -e FLASK_DEBUG=false \
    cccp_dashboard:latest
```

### Test de Connexion
```bash
# Tester la connexion MySQL
python3 -c "import mysql.connector; print('MySQL OK')"

# Tester le binaire cccenter_report
./ccenter_report --help

# Test manuel de l'API
curl http://localhost:5000/api/status
```

## Directives de Style de Code

### Principes Généraux
- Écrire du code clair et auto-documenté avec des docstrings utiles
- Préférer l'explicite au magique ; éviter les effets de bord cachés
- Garder les fonctions focalisées sur une seule responsabilité
- Utiliser des commentaires/docstrings en français là où le code existant les utilise (cohérence)

### Imports
- Imports de la bibliothèque standard en premier, puis tierces parties, puis locaux
- Utiliser des imports absolus (ex: `from config import ...` et non relatifs)
- Grouper les imports par catégorie avec des lignes vides entre les groupes
- Exemple :
  ```python
  import os
  import threading
  from datetime import datetime
  from typing import Dict, List, Optional

  import flask
  from flask import Flask, jsonify
  from flask_cors import CORS

  from config import MYSQL_CONFIG
  from get_users_and_calls import RlogDispatcher
  ```

### Formatage
- Utiliser 4 espaces pour l'indentation (pas de tabulations)
- Longueur maximale de ligne : 120 caractères
- Utiliser des lignes vides pour séparer les sections logiques dans les fonctions
- Placer le docstring du module en haut, après le shebang et l'encodage
- Shebang : `#!/usr/bin/env python3`
- Encodage : `# -*- coding: utf-8 -*-`

### Indicateurs de Types
- Utiliser des indicateurs de types pour les signatures de fonctions (surtout dans `web_server.py`)
- Préférer les types explicites à `Any` quand c'est possible
- Utiliser `Optional[T]` pour les types nullables, pas `T | None` (style existant)
- Exemple :
  ```python
  def get_state(self) -> dict:
      """Obtenir l'état actuel du dashboard"""

  def parse_french_datetime(date_str: str) -> Optional[datetime]:
      """Parser le format de date et retourner un objet datetime"""
  ```

### Conventions de Nommage
- `snake_case` pour les variables, fonctions et méthodes
- `PascalCase` pour les classes (ex: `DashboardState`, `RlogDispatcher`)
- `UPPER_SNAKE_CASE` pour les constantes (ex: `MYSQL_CONFIG`, `DEFAULT_PORT`)
- Préfixer les méthodes/attributs privés avec un underscore (ex: `_auto_refresh`)
- Utiliser des noms descriptifs ; éviter les variables d'une seule lettre sauf pour les compteurs

### Gestion des Erreurs
- Utiliser la journalisation structurée avec `logging.getLogger("cccp")` ou le logger du module
- Journaliser les erreurs avec les niveaux appropriés : `logger.error()`, `logger.warning()`
- Attraper des exceptions spécifiques ; éviter les clauses `except:` nues
- Laisser les exceptions se propager pour les erreurs irrécupérables
- Exemple :
  ```python
  try:
      dispatcher.launch()
  except Exception as e:
      logger.error(f"Erreur lors du démarrage du dispatch en arrière-plan : {e}")
  ```

### Threading et Concurrence
- Utiliser `threading.Lock()` pour la protection de l'état partagé
- Utiliser `threading.Thread()` pour les tâches d'arrière-plan avec daemon=True quand approprié
- Toujours gérer les exceptions dans les boucles de threads pour éviter les échecs silencieux
- Exemple de pattern :
  ```python
  with self.lock:
      # accéder ou modifier l'état partagé
  ```

### Configuration
- Centraliser la config dans `config.py` avec un pattern de dictionnaire
- Supporter les surcharges via variables d'environnement avec des valeurs par défaut raisonnables
- Ne jamais coder en dur les identifiants ; utiliser des placeholders comme `os.getenv("MYSQL_PASSWORD")`
- Le fichier `config.py` sert de source de vérité unique

### Spécifique à Flask
- Utiliser `app.config` pour les paramètres spécifiques à Flask
- Activer CORS avec `CORS(app)` pour les endpoints API
- Utiliser les méthodes HTTP appropriées : GET pour les requêtes, POST pour les changements d'état
- Retourner les réponses JSON avec `jsonify()` pour la cohérence

### Organisation des Fichiers
- Garder les fonctionnalités liées ensemble ; `web_server.py` gère HTTP, `get_users_and_calls.py` gère le protocole CCCP
- Placer les modèles HTML dans le répertoire `templates/`
- Stocker les journaux dans le répertoire `import_logs/`
- Utiliser le script `bash.sh` pour les opérations shell

### Sécurité
- Ne jamais commiter d'identifiants ou de secrets ; utiliser `.gitignore` pour les fichiers sensibles
- Valider et assainir toutes les entrées utilisateur des endpoints API
- Utiliser des requêtes paramétrées (MySQL connector le fait par défaut)
- Suivre le principe du moindre privilège pour les connexions base de données

## Tests

Le projet utilise des tests unitaires avec pytest pour la logique métier.

### Exécuter les tests
```bash
# Installer pytest (si pas encore installé)
pip3 install pytest

# Lancer tous les tests
python3 -m pytest tests/

# Lancer un test spécifique
python3 -m pytest tests/test_fichier.py::ClasseDeTest::test_methode

# Lancer un fichier de test directement
python3 test_call_recovery.py
```

### Écrire des tests
- Utiliser `pytest` comme framework de test
- Placer les tests dans le répertoire `tests/` à la racine
- Nom des fichiers de test : `test_*.py` ou `*_test.py`
- Simuler les dépendances externes (MySQL, serveur CCCP) pour les tests unitaires
- Viser une couverture significative de la logique métier dans `get_users_and_calls.py`

## Notes Supplémentaires

- Le code source utilise des commentaires/docstrings en français ; maintenir la cohérence
- Le binaire `cccenter_report` est un outil propriétaire pour la communication CCCP
- Le projet tourne sur Python 3.8+ ; pas de compatibilité Python 2 nécessaire
- Pas de linting formel configuré ; utiliser `python3 -m py_compile` pour vérifier la syntaxe
- Pour la vérification de types, installer mypy : `pip3 install mypy && mypy web_server.py get_users_and_calls.py config.py`
- Le fichier de test `test_call_recovery.py` peut être lancé directement avec `python3 test_call_recovery.py`
