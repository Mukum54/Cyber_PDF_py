#!/bin/bash
# CYBER PDF - Uninstallation Script

echo "=================================="
echo "CYBER PDF - Uninstallation"
echo "=================================="
echo ""

# Check if installed via pip
if pip show cyber-pdf &> /dev/null; then
    echo "Uninstalling CYBER PDF package..."
    pip uninstall -y cyber-pdf
    echo "✓ Package uninstalled"
else
    echo "CYBER PDF package not found (may not be installed via pip)"
fi

# Remove desktop entry if exists
DESKTOP_FILE="$HOME/.local/share/applications/cyberpdf.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_FILE"
    echo "✓ Desktop entry removed"
fi

# Ask about configuration
echo ""
read -p "Do you want to remove configuration files? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CONFIG_DIR="$HOME/.config/cyberpdf"
    if [ -d "$CONFIG_DIR" ]; then
        echo "Removing configuration directory..."
        rm -rf "$CONFIG_DIR"
        echo "✓ Configuration removed"
    fi
fi

echo ""
echo "=================================="
echo "✓ Uninstallation Complete!"
echo "=================================="
echo ""
