# CYBER PDF - Quick Start Guide

## Installation

The project requires a virtual environment due to system restrictions. Follow these steps:

### 1. Create Virtual Environment

```bash
cd /home/mukum/Desktop/Cyber_PDF
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This may take several minutes as PySide6 is a large package (~170 MB).

### 4. Run the Application

#### GUI Application
```bash
python -m cyberpdf_core.main
```

#### CLI Tool
```bash
# View help
python -m cli.cyberpdf_cli --help

# Example commands
python -m cli.cyberpdf_cli info sample.pdf
python -m cli.cyberpdf_cli split document.pdf --mode by_count --count 10
```

## What's Been Implemented

✅ **Core Backend** (20+ modules, ~3,500 lines of code)
- PDF operations (split, merge, rotate, extract)
- Security (encrypt, decrypt, watermark)
- Page arrangement system
- PDF ↔ Word conversion
- Caching system
- Configuration management

✅ **User Interface**
- Main window with menu/toolbar
- Home dashboard with animated tool cards
- Dark/light theme support
- Keyboard shortcuts

✅ **CLI Tool**
- All major PDF operations
- Batch processing
- Progress indicators

## Testing Without Full Installation

If you want to test the backend without waiting for the full installation:

```bash
# Test configuration system (works without dependencies)
python3 -c "from cyberpdf_core.config import config; print('Config OK:', config.get('general.theme'))"
```

## System Requirements

### Required
- Python 3.10+
- Qt6 libraries (installed via PySide6)

### Optional (for full functionality)
- LibreOffice (for PDF ↔ Word conversion)
- Tesseract (for OCR)
- Ghostscript (for advanced PDF operations)

### Install Optional Dependencies (Debian/Ubuntu)
```bash
sudo apt install libreoffice tesseract-ocr ghostscript
```

## Project Structure

```
Cyber_PDF/
├── cyberpdf_core/      # Backend engine
├── ui/                 # Qt-based interface
├── cli/                # Command-line tool
├── venv/               # Virtual environment
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## Next Steps

1. **Wait for installation to complete** (check with `pip list | grep PySide6`)
2. **Test the GUI**: `python -m cyberpdf_core.main`
3. **Test the CLI**: `python -m cli.cyberpdf_cli --help`
4. **Review the walkthrough**: See `/home/mukum/.gemini/antigravity/brain/.../walkthrough.md`

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### Issue: "No module named 'fitz'"
**Solution**: Install PyMuPDF:
```bash
pip install PyMuPDF
```

### Issue: LibreOffice conversion fails
**Solution**: Install LibreOffice:
```bash
sudo apt install libreoffice
```

## Current Status

The installation is currently in progress. The virtual environment has been created and dependencies are being downloaded. PySide6 (the Qt framework) is a large package and may take several minutes to download and install.

You can monitor the installation progress or wait for it to complete before testing the application.
