# CYBER PDF

<div align="center">

![CYBER PDF Logo](resources/icons/logo.png)

**Professional PDF Operations Suite for Linux**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Qt 6](https://img.shields.io/badge/Qt-6-green.svg)](https://www.qt.io/)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Contributing](#contributing)

</div>

---

## 🚀 Features

### Core Operations
- **📄 PDF ↔ Word Conversion** - Seamless conversion between PDF and DOCX formats
- **✂️ Split & Merge** - Split PDFs by pages, size, or bookmarks; merge multiple PDFs
- **🔄 Page Arrangement** - Visual drag-and-drop page reordering and manipulation
- **🔒 Security** - Encrypt/decrypt PDFs with AES-256, add watermarks
- **📊 Metadata Analytics** - Extract and analyze PDF metadata
- **🔍 Text Extraction** - Extract text content from PDFs
- **🔄 Page Rotation** - Rotate individual or multiple pages

### Advanced Features
- **🤖 Workflow Automation** - Auto-detect optimal operations and batch processing
- **🔌 Plugin System** - Extensible architecture for custom operations
- **🎨 PDF Quality Enhancer** - Deskew, denoise, and improve scanned PDFs
- **👁️ OCR Support** - Extract text from scanned documents (Tesseract)
- **⚡ GPU Acceleration** - Optional GPU support for faster processing
- **💻 CLI Tool** - Full-featured command-line interface

### User Experience
- **🎨 Modern UI** - Beautiful dark/light themes with smooth animations
- **🖱️ Drag & Drop** - Intuitive drag-and-drop everywhere
- **⌨️ Keyboard Shortcuts** - Efficient keyboard navigation
- **🔄 Real-time Preview** - Live preview of operations
- **📱 Responsive Design** - Adapts to different window sizes

---

## 📦 Installation

### AppImage (Recommended)
```bash
# Download the latest AppImage
wget https://github.com/cyberpdf/cyber-pdf/releases/latest/download/CyberPDF-x86_64.AppImage

# Make it executable
chmod +x CyberPDF-x86_64.AppImage

# Run
./CyberPDF-x86_64.AppImage
```

### Flatpak
```bash
flatpak install flathub org.cyberpdf.CyberPDF
flatpak run org.cyberpdf.CyberPDF
```

### Debian/Ubuntu (DEB)
```bash
wget https://github.com/cyberpdf/cyber-pdf/releases/latest/download/cyber-pdf_1.0.0_amd64.deb
sudo dpkg -i cyber-pdf_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies
```

### Arch Linux (AUR)
```bash
yay -S cyber-pdf
# or
yay -S cyber-pdf-git
```

### From Source
```bash
# Clone repository
git clone https://github.com/cyberpdf/cyber-pdf.git
cd cyber-pdf

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m cyberpdf_core.main
```

---

## 🎯 Usage

### GUI Application

Launch the application:
```bash
cyberpdf
```

#### Quick Start
1. **Open the application** - Launch CYBER PDF from your application menu
2. **Choose a tool** - Click on any tool card on the home dashboard
3. **Load your PDF** - Drag and drop or click to browse
4. **Process** - Configure options and click "Apply"
5. **Save** - Export your processed PDF

### Command-Line Interface

```bash
# Split PDF
cyberpdf-cli split document.pdf --pages 1-5 --output part1.pdf

# Merge PDFs
cyberpdf-cli merge file1.pdf file2.pdf file3.pdf --output combined.pdf

# Convert Word to PDF
cyberpdf-cli convert document.docx --to pdf --output result.pdf

# Encrypt PDF
cyberpdf-cli encrypt document.pdf --password mypassword --output secure.pdf

# OCR scanned PDF
cyberpdf-cli ocr scanned.pdf --lang eng --output searchable.pdf

# Batch convert
cyberpdf-cli batch convert *.docx --to pdf --output-dir ./pdfs
```

---

## 🎨 Screenshots

### Home Dashboard
![Home Dashboard](docs/screenshots/home.png)

### Page Arranger
![Page Arranger](docs/screenshots/arranger.png)

### Processing Dialog
![Processing](docs/screenshots/processing.png)

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save/Export |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Ctrl+A` | Select all pages |
| `Delete` | Delete selected pages |
| `Ctrl+T` | Toggle theme |
| `F11` | Fullscreen |

[See all shortcuts](docs/user_guide/shortcuts.md)

---

## 🔧 Configuration

Configuration file location: `~/.config/cyberpdf/config.yaml`

```yaml
general:
  theme: dark
  language: en
  check_updates: true

performance:
  enable_gpu: auto
  thumbnail_cache_size: 500
  max_memory_mb: 1024

security:
  secure_mode: false
  auto_cleanup_temp: true
```

---

## 🔌 Plugin Development

CYBER PDF supports custom plugins. Create your own operations!

```python
from cyberpdf_core.plugins import PluginBase

class MyPlugin(PluginBase):
    name = "My Custom Plugin"
    version = "1.0.0"
    operations = ["custom_operation"]
    
    def execute(self, operation, **kwargs):
        # Your custom logic here
        pass
```

[Plugin Development Guide](docs/developer/plugin_api.md)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Clone repository
git clone https://github.com/cyberpdf/cyber-pdf.git
cd cyber-pdf

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

---

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PyMuPDF** - PDF processing engine
- **PySide6** - Qt bindings for Python
- **Tesseract** - OCR engine
- **OpenCV** - Image processing

---

## 📧 Contact

- **Website**: https://cyberpdf.org
- **GitHub**: https://github.com/cyberpdf/cyber-pdf
- **Issues**: https://github.com/cyberpdf/cyber-pdf/issues
- **Discussions**: https://github.com/cyberpdf/cyber-pdf/discussions

---

<div align="center">

Made with ❤️ by the CYBER PDF Team

⭐ Star us on GitHub if you find this project useful!

</div>
