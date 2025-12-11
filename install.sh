#!/bin/bash
# CYBER PDF - Installation Script

echo "=================================="
echo "CYBER PDF - Installation"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
echo "This may take several minutes..."
echo ""

# Install in stages to handle network issues better
echo "[1/3] Installing core dependencies..."
pip install --no-cache-dir PyMuPDF pypdf python-docx Pillow pycryptodome click PyYAML

echo ""
echo "[2/3] Installing PySide6 (this is large, ~170MB)..."
pip install --no-cache-dir PySide6

echo ""
echo "[3/3] Installing optional dependencies..."
pip install --no-cache-dir pytesseract opencv-python pytest pytest-qt pytest-cov black ruff mypy

echo ""
echo "=================================="
echo "✓ Installation Complete!"
echo "=================================="
echo ""
echo "To run CYBER PDF:"
echo "  source venv/bin/activate"
echo "  python -m cyberpdf_core.main"
echo ""
echo "To use CLI:"
echo "  python -m cli.cyberpdf_cli --help"
echo ""
