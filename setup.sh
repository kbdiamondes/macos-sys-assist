#!/bin/bash
# Setup script for macos-sys-assist MCP server

set -e

echo "=== macos-sys-assist Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "Python $PYTHON_VERSION ✓"

# Create virtual environment
VENV_DIR=".venv"
echo ""
echo "Creating virtual environment in $VENV_DIR..."

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists, skipping creation."
else
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created ✓"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Virtual environment: $(pwd)/$VENV_DIR"
echo "Python executable: $(which python3)"
echo ""
echo "Next steps:"
echo "1. Grant Accessibility permissions:"
echo "   System Settings → Privacy & Security → Accessibility"
echo "   Add this Python interpreter: $(which python3)"
echo ""
echo "2. Edit allowed_apps.json to add your applications"
echo ""
echo "3. Add this server to your opencode.json:"
echo ""
echo '   "mcp": {'
echo '     "macos-sys-assist": {'
echo '       "enabled": true,'
echo '       "command": "'$(pwd)/$VENV_DIR/bin/python3'",'
echo '       "args": ["'$(pwd)'/server.py"]'
echo '     }'
echo '   }'
echo ""
echo "4. Restart OpenCode to load the new MCP server"
echo ""
echo "To activate the virtual environment manually:"
echo "  source $VENV_DIR/bin/activate"
