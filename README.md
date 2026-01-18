# Installation Guide - CCCP Explorer

## Overview

CCCP Explorer is a Python-based tool for exploring and monitoring the CCCP (Consistent Call Center Protocol) server. This document provides complete installation instructions.

## Prerequisites

### System Requirements

- **Python**: 3.6+ (Python 3.14 recommended)
- **Operating System**: Linux (tested on Fedora/CentOS)
- **Network**: Access to CCCP server (default: 10.199.30.67)
- **Disk Space**: ~10 MB for installation

### Installation Modes

#### Option 1: Offline Installation (No Internet Required)

All Python dependencies are included in `installation/packages/`:

```bash
cd /home/fblo/Documents/repos/explo-cst

# Install from local packages (no internet required)
pip install --no-index --find-links=installation/packages -r installation/requirements.txt

# Install CCCP package
pip install -e .
```

Or use the automated script:

```bash
chmod +x installation/setup.sh
./installation/setup.sh --offline
```

#### Option 2: Online Installation (Default)

Installs packages from PyPI (requires internet):

```bash
cd /home/fblo/Documents/repos/explo-cst

# Install dependencies from PyPI
pip install -r installation/requirements.txt

# Install CCCP package
pip install -e .
```

Or use the automated script:

```bash
chmod +x installation/setup.sh
./installation/setup.sh
```

#### Option 3: Using Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r installation/requirements.txt

# Install CCCP package
pip install -e .

# Run
python3 web_server.py
```

## Installation Files

```
/home/fblo/Documents/repos/explo-cst/
├── installation/           # Installation files
│   ├── README.md          # This file
│   ├── QUICK_START.md     # Quick start guide
│   ├── requirements.txt   # Python dependencies list
│   ├── setup.sh           # Automated installation script
│   ├── packages/          # Local Python packages (OFFLINE mode)
│   │   ├── flask-*.whl
│   │   ├── twisted-*.whl
│   │   ├── pyparsing-*.whl
│   │   └── ... (all dependencies)
│   └── DEPLOYMENT.md      # Production deployment guide
├── src/cccp/              # Source code
├── tests/unit-tests/      # Unit tests
├── web_server.py          # Main dashboard server
└── setup.py               # Package setup
```

## Dependencies Included

### Core Packages (in `installation/packages/`)

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.2 | Web framework |
| Flask-CORS | 6.0.2 | CORS support |
| Twisted | 25.5.0 | Async networking |
| pyparsing | 3.3.1 | Parser generator |

### Dependencies of Dependencies

| Package | Version |
|---------|---------|
| attrs | 25.4.0 |
| automat | 25.4.16 |
| blinker | 1.9.0 |
| click | 8.3.1 |
| constantly | 23.10.4 |
| hyperlink | 21.0.0 |
| idna | 3.11 |
| incremental | 24.11.0 |
| itsdangerous | 2.2.0 |
| Jinja2 | 3.1.6 |
| MarkupSafe | 3.0.3 |
| packaging | 25.0 |
| typing_extensions | 4.15.0 |
| Werkzeug | 3.1.5 |
| zope-interface | 8.2.0 |

**Total: 18 packages (~4.5 MB)**
pyparsing>=1.5,<3
Flask>=2.0
Flask-CORS>=3.0
twisted>=18.0
```

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone or navigate to the project directory
cd /home/fblo/Documents/repos/explo-cst

# Install in editable mode
pip install -e .

# Verify installation
python3 -c "import cccp; print('CCCP version:', cccp.__version__)"
```

### Method 2: Using Requirements File

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install from requirements
pip install -r installation/requirements.txt

# Install package
pip install -e .
```

### Method 3: Manual Installation

```bash
# Install each dependency
pip install 'pyparsing>=1.5,<3'
pip install 'Flask>=2.0'
pip install 'Flask-CORS>=3.0'
pip install 'twisted>=18.0'

# Install CCCP package
cd /home/fblo/Documents/repos/explo-cst
pip install -e .
```

## Directory Structure

```
/home/fblo/Documents/repos/explo-cst/
├── installation/           # Installation files
│   ├── README.md          # This file
│   ├── requirements.txt   # Python dependencies
│   ├── setup.sh           # Installation script
│   └── QUICK_START.md     # Quick start guide
├── src/cccp/              # Source code
│   ├── async_module/      # Async protocol implementation
│   ├── conf/              # Configuration modules
│   ├── protocols/         # Protocol definitions
│   ├── sync/              # Sync modules
│   └── usage/             # Usage/API modules
├── tests/unit-tests/      # Unit tests
│   └── test_protocol.py   # Protocol tests
├── web_server.py          # Main dashboard server
├── setup.py               # Package setup
└── AGENTS.md             # Development guidelines
```

## Configuration

### Environment Variables

```bash
# CCCP Server settings (optional, defaults provided)
export CCCP_HOST=10.199.30.67
export CCCP_PROXY_PORT=20101
export CCCP_DISPATCH_PORT=20103

# Application settings
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=False
```

### Server Credentials

Default credentials for CCCP server:

| Service | Host | Port | Username | Password |
|---------|------|------|----------|----------|
| Proxy | 10.199.30.67 | 20101 | supervisor_fdai | toto |
| Dispatch | 10.199.30.67 | 20103 | supervisor_fdai | toto |

## Running the Application

### Start the Dashboard

```bash
# Basic start
python3 /home/fblo/Documents/repos/explo-cst/web_server.py

# With custom settings
CCCP_HOST=10.199.30.67 python3 /home/fblo/Documents/repos/explo-cst/web_server.py
```

### Access the Dashboard

Open a web browser and navigate to:

```
http://localhost:5000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/status` | GET | Current system status |
| `/api/connect` | POST | Connect to CCCP server |
| `/api/events` | GET | Get recent events |
| `/api/events/stream` | GET | SSE stream for real-time events |
| `/api/users` | GET | Get users list |
| `/api/queues` | GET | Get queues list |
| `/api/history` | GET | Get call history |
| `/api/protocol` | GET | Get protocol specification |

## Testing

### Run All Unit Tests

```bash
cd /tmp
PYTHONPATH=/home/fblo/Documents/repos/explo-cst/src python3 -m unittest discover -s /home/fblo/Documents/repos/explo-cst/tests/unit-tests -v
```

### Run Single Test Class

Edit `/home/fblo/Documents/repos/explo-cst/tests/do_one_test.py` to change the import:

```python
from unit_tests.test_protocol import TestCCCPEventParsing  # Change this class
```

Then run:

```bash
python3 /home/fblo/Documents/repos/explo-cst/tests/do_one_test.py
```

### Run Specific Test

```bash
python3 -m unittest unit_tests.test_protocol.TestCCCPEventParsing.test_event_creation -v
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'cccp'
```

**Solution**: Install the package
```bash
pip install -e .
```

#### 2. Connection Refused

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solution**: 
- Verify CCCP server is running
- Check host and port settings
- Verify network connectivity

#### 3. Port Already in Use

```
OSError: [Errno 98] Address already in use
```

**Solution**: Use a different port
```bash
python3 web_server.py --port 5001
```

#### 4. Pyparsing Version Error

```
ImportError: pyparsing version mismatch
```

**Solution**: Install correct version
```bash
pip install 'pyparsing>=1.5,<3'
```

### Debug Mode

Enable debug logging:

```bash
export FLASK_DEBUG=True
python3 /home/fblo/Documents/repos/explo-cst/web_server.py
```

### Log Files

Logs are written to:
- Console output (default)
- `/tmp/cccp.log` (when configured)

## Development

### Code Style

Follow guidelines in `AGENTS.md`:
- Python 2/3 compatible
- 4 spaces indentation
- PascalCase for classes
- snake_case for functions/variables
- Docstrings with `:param type:` annotations

### Adding New Tests

1. Create test file in `tests/unit-tests/`
2. Import from `web_server` or `cccp` modules
3. Use `unittest.TestCase` framework
4. Run tests to verify

### Building Documentation

```bash
# Generate protocol specification
python3 /home/fblo/Documents/repos/explo-cst/analyze_quick.py
```

## Integration with External Systems

### SSH Tunnel for Remote CCCP

```bash
# Create SSH tunnel
ssh -L 20101:10.199.30.67:20101 -L 20103:10.199.30.67:20103 user@gateway

# Then run dashboard locally
python3 /home/fblo/Documents/repos/explo-cst/web_server.py
```

### Docker (Optional)

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 5000
CMD ["python3", "web_server.py"]
```

## Security Considerations

- **Credentials**: Store in environment variables, not in code
- **Network**: Use VPN or SSH tunnel for remote connections
- **Firewall**: Only expose necessary ports (5000 for web UI)
- **Updates**: Keep dependencies updated

## Support

For issues and questions:
1. Check troubleshooting section
2. Review test output for error details
3. Check CCCP server logs
4. Report issues with:
   - Error messages
   - Steps to reproduce
   - Environment details

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01 | Initial release |
| 1.4.6 | 2024-01 | Current version |

## License

This software is part of Interact-IV's CCCP Library.
Contact: softeam@interact-iv.com
