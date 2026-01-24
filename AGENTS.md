# AGENTS.md - Dashboard CCC Report

## Commandes de Build

### Build Conteneur
```bash
# Build optimisé (recommandé) - 310 MB (-26% vs original)
podman build -f Containerfile.minimal -t cccp_dashboard:latest .

# Build original - 418 MB
podman build -f Containerfile.test -t cccp_dashboard:original .

# Build sans cache pour un build propre
podman build --no-cache -f Containerfile.minimal -t cccp_dashboard:latest .
```

### Commandes Développement
```bash
# Lancer le dashboard web localement
python3 web_server.py

# Installer les dépendances Python
pip3 install -r requirements.txt

# Tester la connexion MySQL
python3 -c "import mysql.connector; conn = mysql.connector.connect(host='vs-ics-prd-web-fr-505', user='interactiv', password='ics427!'); print('✅ MySQL OK'); conn.close()"

# Tester le binaire cccenter_report localement
./ccenter_report --version
```

### Commandes Runtime
```bash
# Lancer le conteneur avec dashboard web
podman run --rm -p 5000:5000 \
    -e MYSQL_HOST=vs-ics-prd-web-fr-505 \
    -e MYSQL_USER=interactiv \
    -e MYSQL_PASSWORD=ics427! \
    -e DEFAULT_SERVER_IP=10.199.30.67 \
    -e DEFAULT_SERVER_PORT=20103 \
    cccp_dashboard:latest

# Tester le binaire depuis le conteneur
podman run --rm cccp_dashboard:latest /app/ccenter_report --version
```

## Commandes de Test

### Tests Manuels
Ce projet utilise des tests manuels :

```bash
# Tester l'API du dashboard web
curl http://localhost:5000/api/status

# Tester les différentes routes
curl http://localhost:5000/api/users
curl http://localhost:5000/api/calls
curl http://localhost:5000/

# Tester la connectivité MySQL
python3 -c "
import mysql.connector
try:
    conn = mysql.connector.connect(host='vs-ics-prd-web-fr-505', user='interactiv', password='ics427!')
    print('✅ Connexion MySQL réussie')
    conn.close()
except Exception as e:
    print(f'❌ Erreur MySQL: {e}')
"

# Valider le binaire cccenter_report
./ccenter_report --help
```

## Directives de Style de Code

### Style Python (Dashboard Web)
- **Structure**: Application Flask monolithique avec threading
- **Imports**: Bibliothèque standard d'abord, puis tierces (flask, mysql-connector)
- **Nommination**: snake_case pour variables/fonctions, PascalCase pour classes
- **Type Hints**: Utiliser typing module (Dict, List, Optional) pour signatures
- **Gestion d'erreurs**: try/except avec logging, éviter bare except
- **Documentation**: Docstrings pour classes et fonctions principales
- **Routes Flask**: Noms descriptifs avec méthodes HTTP appropriées
- **Threading**: Utiliser threading.Lock() pour les données partagées

### Structure des Templates HTML
- **Thèmes**: Versions light et dark pour chaque template
- **Modern Dashboard**: Interface principale avec temps réel
- **Console Minimal**: Interface simplifiée pour opérations
- **Index**: Page d'accueil et navigation

### Variables d'Environnement
```bash
# Configuration application
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Base de données MySQL
MYSQL_HOST=vs-ics-prd-web-fr-505
MYSQL_USER=interactiv
MYSQL_PASSWORD=ics427!
MYSQL_DATABASE= (optionnel)

# Serveur CCCP par défaut
DEFAULT_SERVER_IP=10.199.30.67
DEFAULT_SERVER_PORT=20103
```

## Architecture du Projet

### Structure Simplifiée
```
/                             # Racine du projet
├── ccenter_report            # Binaire C++ compilé (exécutable)
├── web_server.py            # Dashboard Flask principal
├── get_users_and_calls.py   # Script de récupération MySQL
├── requirements.txt         # Dépendances Python
├── Containerfile.test       # Configuration conteneur runtime
├── AGENTS.md                # Documentation pour agents
├── .gitignore               # Fichiers ignorés par Git
└── templates/               # Templates HTML
    ├── index.html
    ├── modern_dashboard.html
    ├── modern_dashboard_light.html
    ├── console_minimal.html
    └── console_minimal_light.html
```

### Composants Principaux
- **ccenter_report**: Binaire ELF 64-bit pour communication CCCP (1.1MB)
- **web_server.py**: Application Flask avec APIs REST temps réel
- **get_users_and_calls.py**: Connecteur MySQL pour données utilisateurs
- **Templates/**: Interfaces HTML modernes avec thèmes multiples

### Conteneur Runtime Optimisé
- **Base**: Fedora 39 minimaliste (310 MB, -26% vs original)
- **Binaire**: cccenter_report copié dans /app
- **Web**: Flask server sur port 5000
- **Config**: Fichier config.py généré automatiquement
- **Dépendances**: flask, flask-cors, mysql-connector-python
- **Sécurité**: Utilisateur non-root (cccp:1000)
- **Performance**: Variables Python optimisées

### Dépendances Clés
- **Python**: Flask>=2.0.0, flask-cors>=3.0.0, mysql-connector-python>=8.0.0
- **Système**: mysql, mariadb-connector-c, libxml2, libxslt, libxcrypt
- **Runtime**: Python 3, glibc 2.38+, curl, wget

### Flux de Données
1. **MySQL** → get_users_and_calls.py → web_server.py → Dashboard
2. **CCCP Server** ← ccenter_report ← web_server.py (via subprocess)
3. **Dashboard** ← WebSocket temps réel ← Flask APIs

## Bonnes Pratiques

### Sécurité
- Les mots de passe MySQL sont dans les variables d'environnement
- Le conteneur expose uniquement le port 5000
- Utilisation de CORS pour contrôler les origines autorisées

### Performance
- Threading pour les opérations asynchrones
- Cache Jinja2 désactivé pour le développement
- Connection pooling MySQL recommandé pour la production

### Développement
- .gitignore exclut __pycache__ et sessions
- Structure plate pour simplifier le déploiement
- Binaire pré-compilé pour éviter les dépendances de build