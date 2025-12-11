# Building and Distributing CYBER PDF

This guide explains how to build distribution packages for CYBER PDF.

## Prerequisites

```bash
# Install build tools
pip install build twine
```

## Building Python Packages

### 1. Build Wheel and Source Distribution

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build the package
python -m build

# This creates:
# - dist/cyber_pdf-1.0.0-py3-none-any.whl (wheel package)
# - dist/cyber-pdf-1.0.0.tar.gz (source distribution)
```

### 2. Verify the Build

```bash
# Check package contents
tar -tzf dist/cyber-pdf-1.0.0.tar.gz

# Test installation in a clean environment
python -m venv test_env
source test_env/bin/activate
pip install dist/cyber_pdf-1.0.0-py3-none-any.whl
cyberpdf --version
deactivate
rm -rf test_env
```

## Distribution Methods

### Method 1: GitHub Releases

1. **Create a Git Tag**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create GitHub Release**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Select the tag `v1.0.0`
   - Upload the files from `dist/`:
     - `cyber_pdf-1.0.0-py3-none-any.whl`
     - `cyber-pdf-1.0.0.tar.gz`
   - Add release notes

3. **Users can install via**:
   ```bash
   pip install https://github.com/Mukum54/Cyber_PDF_py/releases/download/v1.0.0/cyber_pdf-1.0.0-py3-none-any.whl
   ```

### Method 2: PyPI (Python Package Index)

**Note**: Requires a PyPI account

```bash
# Test on TestPyPI first
python -m twine upload --repository testpypi dist/*

# If successful, upload to PyPI
python -m twine upload dist/*
```

Users can then install via:
```bash
pip install cyber-pdf
```

### Method 3: Direct Download

Host the wheel file on your website or file sharing service:

```bash
# Users download and install
wget https://your-site.com/cyber_pdf-1.0.0-py3-none-any.whl
pip install cyber_pdf-1.0.0-py3-none-any.whl
```

## Creating an Installation Script for Users

Create a simple one-liner for users:

```bash
# install-cyberpdf.sh
#!/bin/bash
pip install https://github.com/Mukum54/Cyber_PDF_py/releases/download/v1.0.0/cyber_pdf-1.0.0-py3-none-any.whl
```

Users can run:
```bash
curl -sSL https://raw.githubusercontent.com/Mukum54/Cyber_PDF_py/main/install-cyberpdf.sh | bash
```

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
name = "cyber-pdf"
version = "1.0.1"  # Update this
```

## Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run tests: `pytest`
- [ ] Build packages: `python -m build`
- [ ] Test installation in clean environment
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] Create GitHub release
- [ ] Upload distribution files
- [ ] Update documentation

## File Size Optimization

The wheel package includes only necessary files thanks to `MANIFEST.in`:

```
Typical sizes:
- Wheel (.whl): ~50-100 KB (code only)
- Source (.tar.gz): ~100-200 KB (includes docs)
- Dependencies: ~200 MB (PySide6 is large)
```

## Testing the Package

```bash
# Create test environment
python -m venv test_install
source test_install/bin/activate

# Install from wheel
pip install dist/cyber_pdf-1.0.0-py3-none-any.whl

# Test CLI
cyberpdf --version
cyberpdf-cli --help

# Test GUI
cyberpdf

# Cleanup
deactivate
rm -rf test_install
```

## Continuous Integration (Optional)

Add GitHub Actions to automate builds:

Create `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install build tools
        run: pip install build
      - name: Build package
        run: python -m build
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
```

This automatically builds and uploads packages when you push a tag.
