# Quick Start Guide - CCCP Explorer

## 5-Minute Setup

### Offline Installation (No Internet)

```bash
cd /home/fblo/Documents/repos/explo-cst

# Install from local packages (no internet required)
pip install --no-index --find-links=installation/packages -r installation/requirements.txt

# Install CCCP package
pip install -e .

# Run dashboard
python3 web_server.py
```

### Online Installation (Default)

```bash
cd /home/fblo/Documents/repos/explo-cst

# Install dependencies
pip install -r installation/requirements.txt

# Install CCCP package
pip install -e .

# Run dashboard
python3 web_server.py
```

### Automated Installation

```bash
cd /home/fblo/Documents/repos/explo-cst

# Make script executable
chmod +x installation/setup.sh

# Offline mode (no internet)
./installation/setup.sh --offline

# OR online mode (default)
./installation/setup.sh
```

### Access Dashboard

Open browser: **http://localhost:5000**

## Common Commands

### Installation

| Command | Description |
|---------|-------------|
| `pip install -e .` | Install package in editable mode |
| `pip install --no-index --find-links=installation/packages -r installation/requirements.txt` | Offline install |
| `./installation/setup.sh` | Automated install (online) |
| `./installation/setup.sh --offline` | Automated install (offline) |
| `./installation/setup.sh --venv` | Install with virtual environment |

### Testing

| Command | Description |
|---------|-------------|
| `PYTHONPATH=/home/fblo/Documents/repos/explo-cst/src python3 -m unittest discover -s /home/fblo/Documents/repos/explo-cst/tests/unit-tests -v` | Run all tests |
| `python3 tests/do_one_test.py` | Run single test class |
| `./installation/setup.sh --test` | Install and run tests |

### Running

| Command | Description |
|---------|-------------|
| `python3 web_server.py` | Start dashboard (default port 5000) |
| `python3 web_server.py --port 8080` | Start on custom port |
| `FLASK_DEBUG=True python3 web_server.py` | Start with debug logging |

## Default Configuration

```
CCCP Server Host:     10.199.30.67
CCCP Proxy Port:      20101
CCCP Dispatch Port:   20103
Dashboard Port:       5000
Username:             supervisor_fdai
Password:             toto
```

## Packages Included (No Download Needed)

All Python dependencies are included in `installation/packages/`:

- Flask 3.1.2
- Flask-CORS 6.0.2
- Twisted 25.5.0
- pyparsing 3.3.1
- + 14 sub-dependencies

**Total: 18 wheel files (~4.5 MB)**

## API Quick Reference

```bash
# Get system status
curl http://localhost:5000/api/status

# Get users list
curl http://localhost:5000/api/users

# Get queues list
curl http://localhost:5000/api/queues

# Get call history
curl http://localhost:5000/api/history

# Get recent events
curl http://localhost:5000/api/events

# Get protocol spec
curl http://localhost:5000/api/protocol
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found: cccp" | Run `pip install -e .` |
| Connection refused | Check CCCP server is running |
| Port 5000 in use | Use `--port 5001` |
| Login failed | Verify credentials |
| No internet | Use `--offline` mode with local packages |

## Next Steps

1. Read the full [Installation Guide](README.md)
2. Explore the [API Documentation](README.md#api-endpoints)
3. Run the unit tests to verify installation
4. Check out the source code in `src/cccp/`

## Need Help?

- Full documentation: [installation/README.md](README.md)
- Check troubleshooting section in README
- Review test output for error details
