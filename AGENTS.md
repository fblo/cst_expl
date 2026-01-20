# AGENTS.md - CCCP Explorer Development Guide

## Running the Server
```bash
pip install -r requirements.txt  # Install dependencies
python3 web_server.py            # Start Flask server (default port 5000)
python3 get_users_and_calls.py   # Run standalone data fetch script
```

## Code Style Guidelines
- **Imports**: Stdlib first, then third-party (flask, flask_cors), use explicit imports
- **Naming**: snake_case for functions/variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants
- **Types**: Use type hints from `typing` module, dataclasses for structured data, IntEnum for enums
- **Formatting**: 4-space indentation, 120-char line limit, blank lines between class definitions
- **Error Handling**: Use try/except with specific exceptions, log errors via `logger`, include context
- **Logging**: Use `logger = logging.getLogger("cccp")`, log at appropriate levels (INFO, DEBUG, ERROR)
- **Threading**: Use threading.Lock() for shared state, daemon threads for background tasks
- **Documentation**: Docstrings for all public classes/functions, explain parameters and return values

## Linting (if added)
```bash
pip install ruff
ruff check .          # Run linter
ruff format .         # Auto-format code
```
