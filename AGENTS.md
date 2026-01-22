# AGENTS.md - CCCP Explorer Development Guide

## Running the Server
```bash
pip install -r requirements.txt  # Install dependencies
python3 web_server.py            # Start Flask server (default port 5000)
python3 get_users_and_calls.py   # Run standalone data fetch script
ruff check . && ruff format .    # Lint and format code
```

## Code Style Guidelines
- **Imports**: Stdlib first, then third-party (flask, flask_cors), explicit imports
- **Naming**: snake_case for functions/vars, PascalCase for classes, SCREAMING_SNAKE_CASE for constants
- **Types**: Use `typing` module, dataclasses for structured data, IntEnum for enums
- **Formatting**: 4-space indent, 120-char line limit, blank lines between class definitions
- **Error Handling**: try/except with specific exceptions, log via `logger`, include context
- **Logging**: `logger = logging.getLogger("cccp")`, use INFO/DEBUG/ERROR levels appropriately
- **Threading**: Use threading.Lock() for shared state, daemon threads for background tasks
- **Documentation**: Docstrings for all public classes/functions, explain params and return values
