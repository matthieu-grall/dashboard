#!/bin/bash
# =============================================================================
# install.sh
# One-time setup script. Run this once before using the dashboard.
# Creates a Python virtual environment, installs dependencies, and generates
# the first dashboard.json so the page is ready to display immediately.
#
# Usage:
#   cd /path/to/dashboard
#   bash install.sh
# =============================================================================

# Resolve the project directory from the script's own location
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=== Dashboard — initial setup ==="
echo "Project directory: $DIR"

# Create data/ folder if it does not exist yet
mkdir -p data

# Create the Python virtual environment inside the project folder
echo ""
echo "--- Creating virtual environment..."
python3 -m venv venv

# Install required Python packages into the venv
echo ""
echo "--- Installing Python dependencies..."
venv/bin/pip install --upgrade pip
venv/bin/pip install requests feedparser

# Make start.sh executable
chmod +x start.sh

# Run update.py once to generate data/dashboard.json
echo ""
echo "--- Fetching initial data..."
venv/bin/python update.py

echo ""
echo "=== Setup complete ==="
echo "Double-click dashboard.desktop to launch the dashboard."