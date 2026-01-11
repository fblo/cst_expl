# AGENTS.md

## Commandes de build et test
- Installation: `pip install -e .` (requiert pyparsing>=1.5,<3)
- Exécuter les tests unitaires: `cd /tmp && PYTHONPATH=/home/fblo/Documents/repos/iv-cccp/src python3 -m unittest discover -s /home/fblo/Documents/repos/iv-cccp/tests/unit-tests -v`
- Exécuter un seul test unitaire: Modifier `tests/do_one_test.py` pour importer la classe souhaitée depuis `unit_tests/`, puis exécuter `python3 tests/do_one_test.py`
- Tests d'intégration: Nécessitent un serveur CCC réel (`python tests/do_tests.py`)

## Serveur Web Monitoring
- Lancer le dashboard: `python3 web_server.py [port]`
- Dashboard: http://localhost:5000
- API REST: http://localhost:5000/api/{status,queues,users,sessions,events,projects,errors}
- WebSocket: Connexion automatique pour mises à jour temps réel

## Conventions de code
- Code compatible Python 2/3 (pas de type hints, hériter de `object`)
- Utiliser 4 espaces pour l'indentation
- Inclure un en-tête: shebang, encodage, copyright, contact, auteurs
- Noms de classes: PascalCase (ex: `BaseCcxmlClient`)
- Fonctions/variables: snake_case (ex: `get_login_ok`)
- Docstrings: Utiliser les annotations `:param type:` et `:raises:`
- Imports: stdlib, tiers, local (ligne vide entre les groupes)
- Gestion des erreurs: Lever des exceptions descriptives avec contexte
