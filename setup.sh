#!/bin/bash
# =============================================================================
# CCCP Explorer - Installation Script
# =============================================================================
# This script automates the installation process for CCCP Explorer.
# Supports both online and offline installation.
#
# Usage:
#   chmod +x installation/setup.sh
#   ./installation/setup.sh
#
# Options:
#   --help     Show this help message
#   --offline  Install from local packages (no internet required)
#   --online   Install from PyPI (default, requires internet)
#   --venv     Create and use a virtual environment
#   --test     Run tests after installation
#   --clean    Clean build artifacts before installing
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"
PYTHON_CMD="${PYTHON_CMD:-python3}"
PACKAGES_DIR="${PROJECT_DIR}/installation/packages"

# Parse arguments
OFFLINE_INSTALL=false
ONLINE_INSTALL=true
CREATE_VENV=false
RUN_TESTS=false
CLEAN_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            head -30 "$0" | tail -15
            echo ""
            echo "Options:"
            echo "  --help     Show this help message"
            echo "  --offline  Install from local packages (no internet)"
            echo "  --online   Install from PyPI (default)"
            echo "  --venv     Create and use virtual environment"
            echo "  --test     Run tests after installation"
            echo "  --clean    Clean build artifacts before installing"
            exit 0
            ;;
        --offline)
            OFFLINE_INSTALL=true
            ONLINE_INSTALL=false
            shift
            ;;
        --online)
            OFFLINE_INSTALL=false
            ONLINE_INSTALL=true
            shift
            ;;
        --venv)
            CREATE_VENV=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

# Banner
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           CCCP Explorer - Installation Script              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ $OFFLINE_INSTALL == true ]]; then
    print_info "Mode: OFFLINE (using local packages)"
else
    print_info "Mode: ONLINE (downloading from PyPI)"
fi

# Step 1: Check Python version
print_step "Checking Python installation..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Python not found. Please install Python 3.6+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major, sys.version_info.minor)')
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d' ' -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d' ' -f2)

if [[ $MAJOR_VERSION -lt 3 ]] || [[ $MAJOR_VERSION -eq 3 && $MINOR_VERSION -lt 6 ]]; then
    print_error "Python 3.6+ required. Found: $MAJOR_VERSION.$MINOR_VERSION"
    exit 1
fi

print_info "Python $MAJOR_VERSION.$MINOR_VERSION found"

# Step 2: Create virtual environment if requested
if [[ $CREATE_VENV == true ]]; then
    print_step "Creating virtual environment..."
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists. Using existing one."
    else
        $PYTHON_CMD -m venv $VENV_DIR
        print_info "Virtual environment created at: $VENV_DIR"
    fi
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    print_info "Virtual environment activated"
    
    # Upgrade pip
    print_step "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
fi

# Step 3: Clean build artifacts if requested
if [[ $CLEAN_BUILD == true ]]; then
    print_step "Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info/ *.whl 2>/dev/null || true
    rm -rf src/cccp/__pycache__/ src/cccp/*/__pycache__/ 2>/dev/null || true
    rm -rf tests/unit-tests/__pycache__/ 2>/dev/null || true
    print_info "Build artifacts cleaned"
fi

# Step 4: Install dependencies
print_step "Installing Python dependencies..."

if [[ $OFFLINE_INSTALL == true ]]; then
    # Check if packages exist
    if [[ ! -d "$PACKAGES_DIR" ]] || [[ -z "$(ls -A $PACKAGES_DIR/*.whl 2>/dev/null)" ]]; then
        print_error "No packages found in $PACKAGES_DIR"
        print_info "Please run with --online or download packages manually"
        exit 1
    fi
    
    # Install from local packages
    pip install --no-index --find-links="$PACKAGES_DIR" -r "$PROJECT_DIR/installation/requirements.txt" || {
        print_error "Failed to install from local packages"
        exit 1
    }
else
    # Install from PyPI
    pip install -q 'pyparsing>=1.5,<3' || {
        print_error "Failed to install pyparsing"
        exit 1
    }
    pip install -q 'Flask>=2.0' || {
        print_error "Failed to install Flask"
        exit 1
    }
    pip install -q 'Flask-CORS>=3.0' || {
        print_error "Failed to install Flask-CORS"
        exit 1
    }
    pip install -q 'twisted>=18.0' || {
        print_error "Failed to install Twisted"
        exit 1
    }
fi

print_info "Dependencies installed successfully"

# Step 5: Install CCCP package
print_step "Installing CCCP Explorer package..."
cd "$PROJECT_DIR"
pip install -q -e . || {
    print_error "Failed to install CCCP package"
    exit 1
}
print_info "CCCP Explorer installed successfully"

# Step 6: Verify installation
print_step "Verifying installation..."
if $PYTHON_CMD -c "import cccp" 2>/dev/null; then
    print_info "CCCP module imported successfully"
else
    print_error "Failed to import CCCP module"
    exit 1
fi

# Step 7: Run tests if requested
if [[ $RUN_TESTS == true ]]; then
    print_step "Running unit tests..."
    cd /tmp
    PYTHONPATH="$PROJECT_DIR/src" $PYTHON_CMD -m unittest discover -s "$PROJECT_DIR/tests/unit-tests" -v 2>&1
    
    if [[ $? -eq 0 ]]; then
        print_info "All tests passed!"
    else
        print_warning "Some tests failed"
    fi
fi

# Final message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Installation Complete!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "To start the CCCP Explorer dashboard:"
echo -e "  ${YELLOW}python3 ${PROJECT_DIR}/web_server.py${NC}"
echo ""
echo -e "To access the dashboard:"
echo -e "  ${YELLOW}http://localhost:5000${NC}"
echo ""
echo -e "For more information, see: ${YELLOW}${PROJECT_DIR}/installation/README.md${NC}"
echo ""
