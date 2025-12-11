# CYBER PDF - Installation Guide

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+, Fedora 35+, Arch Linux, or equivalent)
- **Python**: 3.10 or higher
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 500 MB for application + dependencies

### Required System Packages
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

---

## Installation Methods

### Method 1: Quick Install Script (Recommended)

Download and run the installation script:

```bash
# Clone the repository
git clone https://github.com/Mukum54/Cyber_PDF_py.git
cd Cyber_PDF_py

# Run the installation script
./install.sh
```

The script will:
- Create a virtual environment
- Install all dependencies
- Set up the application

**To run after installation:**
```bash
source venv/bin/activate
python -m cyberpdf_core.main
```

---

### Method 2: Install with pip (System-wide)

```bash
# Clone the repository
git clone https://github.com/Mukum54/Cyber_PDF_py.git
cd Cyber_PDF_py

# Install the package
pip install .

# Or install in editable mode for development
pip install -e .
```

**To run:**
```bash
cyberpdf
```

---

### Method 3: Manual Installation

```bash
# Clone the repository
git clone https://github.com/Mukum54/Cyber_PDF_py.git
cd Cyber_PDF_py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m cyberpdf_core.main
```

---

## Desktop Integration

To add CYBER PDF to your application menu:

```bash
# Copy desktop entry
mkdir -p ~/.local/share/applications
cp cyberpdf.desktop ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

Now you can launch CYBER PDF from your application menu!

---

## Optional Features

### OCR Support (Text Recognition)

To enable OCR for scanned PDFs:

```bash
# Install Tesseract OCR
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Fedora
sudo dnf install tesseract tesseract-langpack-eng

# Arch Linux
sudo pacman -S tesseract tesseract-data-eng

# Install Python packages
pip install pytesseract opencv-python
```

---

## Building Distribution Packages

### Build Python Wheel

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/cyber_pdf-1.0.0-py3-none-any.whl
# - dist/cyber-pdf-1.0.0.tar.gz
```

### Install from Wheel

```bash
pip install dist/cyber_pdf-1.0.0-py3-none-any.whl
```

---

## Uninstallation

### Using the Uninstall Script

```bash
./uninstall.sh
```

### Manual Uninstallation

```bash
# If installed via pip
pip uninstall cyber-pdf

# Remove desktop entry
rm ~/.local/share/applications/cyberpdf.desktop

# Remove configuration (optional)
rm -rf ~/.config/cyberpdf
```

---

## Troubleshooting

### Python Version Issues

**Error**: `Python 3.10 or higher is required`

**Solution**:
```bash
# Check your Python version
python3 --version

# If too old, install Python 3.10+
# Ubuntu 20.04
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv
```

### PySide6 Installation Issues

**Error**: `Failed to install PySide6`

**Solution**:
```bash
# Install system dependencies first
# Ubuntu/Debian
sudo apt-get install qt6-base-dev libgl1-mesa-dev

# Then retry
pip install PySide6
```

### Permission Errors

**Error**: `Permission denied` when installing

**Solution**:
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR install with --user flag
pip install --user -r requirements.txt
```

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'fitz'`

**Solution**:
```bash
pip install PyMuPDF
```

---

## Verifying Installation

Test that everything is working:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run the application
python -m cyberpdf_core.main

# Or if installed system-wide
cyberpdf
```

You should see the CYBER PDF main window appear.

---

## Updating

### From Git Repository

```bash
cd Cyber_PDF_py
git pull origin main

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### From pip

```bash
pip install --upgrade cyber-pdf
```

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [QUICKSTART.md](QUICKSTART.md) guide
3. Open an issue on [GitHub](https://github.com/Mukum54/Cyber_PDF_py/issues)
4. Include:
   - Your OS and version
   - Python version (`python3 --version`)
   - Error messages
   - Steps to reproduce

---

## Next Steps

After installation:

1. Read the [QUICKSTART.md](QUICKSTART.md) guide
2. Explore the features in [FUNCTIONAL_SCREENS.md](FUNCTIONAL_SCREENS.md)
3. Try the sample operations
4. Check out the CLI tools: `cyberpdf-cli --help`

Enjoy using CYBER PDF! 🚀
