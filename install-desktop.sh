#!/bin/bash

set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run with sudo to install system-wide."
    echo "Usage: sudo ./install-desktop.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="/usr/share/applications"

echo "Installing Pangolin 11 Fan Control GUI..."

# Install required Python packages
echo "Installing Python dependencies..."
# Try with --break-system-packages first (for newer systems), then fallback to regular install
if ! pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages 2>/dev/null; then
    echo "Falling back to regular pip install..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

# Create directories if they don't exist
mkdir -p "$ICON_DIR"
mkdir -p "$DESKTOP_DIR"

# Copy the application files
echo "Copying application files..."
cp "$SCRIPT_DIR/pang11-fancontrol-gui" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/pang11-fancontrol-main.py"
cp "$SCRIPT_DIR/fan.png" "$INSTALL_DIR/"

# Copy icon
echo "Installing icon..."
cp "$SCRIPT_DIR/fan.png" "$ICON_DIR/pang11-fancontrol.png"

# Update the wrapper script to point to the installed location
sed -i "s|main_script = os.path.join(script_dir, \"main.py\")|main_script = os.path.join(script_dir, \"pang11-fancontrol-main.py\")|" "$INSTALL_DIR/pang11-fancontrol-gui"

# Make sure the installed script is executable
chmod +x "$INSTALL_DIR/pang11-fancontrol-gui"

# Install desktop entry
echo "Installing desktop entry..."
cp "$SCRIPT_DIR/pang11-fancontrol.desktop" "$DESKTOP_DIR/"

# Update icon cache
echo "Updating icon cache..."
gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true

# Update desktop database
echo "Updating desktop database..."
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo "Installation complete!"
echo ""
echo "The Pangolin 11 Fan Control application should now appear in your applications menu."
echo "You can also run it from the command line with: pang11-fancontrol-gui"
echo ""
echo "Note: The application will automatically request sudo privileges when launched."
