#!/bin/bash
set -e  # Stop on error

echo "🧪 Initializing Protocol Environment..."

# 1. Ensure pip is up to date
echo "🆙 Upgrading pip..."
python3 -m pip install --upgrade pip

# 2. Install the package and dependencies
# -e installs in 'editable' mode (useful for development)
# . refers to the current directory containing pyproject.toml
echo "📦 Installing Protocol Bot and dependencies (Pandas, OpenPyXL, etc.)..."
pip install -e .

echo "✅ Setup Complete! All dependencies from pyproject.toml are installed."