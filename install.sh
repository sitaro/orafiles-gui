#!/usr/bin/env bash
set -euo pipefail

APP_NAME="orafiles-gui"
MIN_PYTHON="3.9"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# --- Find Python >= 3.9 ---
find_python() {
    for cmd in python3 python python3.11 python3.12 python3.10 python3.9; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) || continue
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# --- Check tkinter availability ---
check_tkinter() {
    "$1" -c "import tkinter" 2>/dev/null
}

# --- Main ---
echo ""
echo "  OraFiles GUI - Installer"
echo "  ========================"
echo ""

# Find Python
PYTHON=$(find_python) || error "Python >= ${MIN_PYTHON} not found. Please install Python 3.9 or later."
PYTHON_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
info "Found Python ${PYTHON_VER} ($(command -v "$PYTHON"))"

# Check tkinter
if ! check_tkinter "$PYTHON"; then
    error "tkinter is not available for ${PYTHON}.
    On macOS:   brew install python-tk
    On Debian:  sudo apt install python3-tk
    On Fedora:  sudo dnf install python3-tkinter"
fi
info "tkinter is available"

# Determine install mode
echo ""
echo "  Install options:"
echo "    1) Install into virtual environment (recommended)"
echo "    2) Install system-wide (pip install .)"
echo "    3) Development install (pip install -e .)"
echo ""
read -rp "  Choose [1/2/3] (default: 1): " choice
choice="${choice:-1}"

case "$choice" in
    1)
        VENV_DIR="${SCRIPT_DIR}/.venv"
        if [ -d "$VENV_DIR" ]; then
            warn "Virtual environment already exists at ${VENV_DIR}"
            read -rp "  Recreate? [y/N]: " recreate
            if [[ "$recreate" =~ ^[Yy]$ ]]; then
                rm -rf "$VENV_DIR"
            fi
        fi

        if [ ! -d "$VENV_DIR" ]; then
            info "Creating virtual environment..."
            "$PYTHON" -m venv "$VENV_DIR"
        fi

        info "Activating virtual environment..."
        source "${VENV_DIR}/bin/activate"

        info "Upgrading pip..."
        pip install --upgrade pip --quiet

        info "Installing ${APP_NAME}..."
        pip install "${SCRIPT_DIR}" --quiet

        echo ""
        info "Installation complete!"
        echo ""
        echo "  To run:"
        echo "    source ${VENV_DIR}/bin/activate"
        echo "    orafiles-gui"
        echo ""
        echo "  Or directly:"
        echo "    ${VENV_DIR}/bin/orafiles-gui"
        echo ""
        ;;
    2)
        info "Installing ${APP_NAME} system-wide..."
        if ! "$PYTHON" -m pip install "${SCRIPT_DIR}" --quiet 2>/dev/null; then
            warn "System install failed (PEP 668). Trying --user install..."
            "$PYTHON" -m pip install "${SCRIPT_DIR}" --user --quiet
        fi
        info "Installation complete! Run with: orafiles-gui"
        ;;
    3)
        info "Installing ${APP_NAME} in development mode..."
        if ! "$PYTHON" -m pip install -e "${SCRIPT_DIR}" --quiet 2>/dev/null; then
            warn "System install failed (PEP 668). Trying --user install..."
            "$PYTHON" -m pip install -e "${SCRIPT_DIR}" --user --quiet
        fi
        info "Installation complete! Run with: orafiles-gui"
        ;;
    *)
        error "Invalid choice: ${choice}"
        ;;
esac
