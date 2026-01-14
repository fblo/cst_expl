# AGENTS.md

## Build and test commands
- Installation: `pip install -e .` (requires pyparsing>=1.5,<3)
- Run unit tests: `cd /tmp && PYTHONPATH=/home/fblo/Documents/repos/explo-cst/src python3 -m unittest discover -s /home/fblo/Documents/repos/explo-cst/tests/unit-tests -v`
- Run single test: Modify `tests/do_one_test.py` to import desired class from `unit-tests/`, then run `python3 tests/do_one_test.py`
- Integration tests: Require real CCC server (`python3 tests/do_tests.py`)

## Code style guidelines
- Python 2/3 compatible (no type hints, inherit from `object`)
- Use 4 spaces for indentation
- Include header: shebang, encoding, copyright, contact, authors
- Class names: PascalCase (ex: `BaseCcxmlClient`)
- Functions/variables: snake_case (ex: `get_login_ok`)
- Docstrings: Use `:param type:` and `:raises:` annotations
- Imports: stdlib, third-party, local (blank line between groups)
- Error handling: Raise descriptive exceptions with context
- File structure: Main source in `src/cccp/`, tests in `tests/unit-tests/`
