#!/bin/bash

echo "Installing Clevo Fan Control GUI dependencies..."

# Install tkinter (python3-tk) based on the distribution
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    echo "Installing python3-tk for Debian/Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y python3-tk
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Installing python3-tkinter for Fedora..."
    sudo dnf install -y python3-tkinter
elif command -v pacman &> /dev/null; then
    # Arch
    echo "Installing tk for Arch Linux..."
    sudo pacman -S --noconfirm tk
elif command -v zypper &> /dev/null; then
    # openSUSE
    echo "Installing python3-tk for openSUSE..."
    sudo zypper install -y python3-tk
else
    echo "Could not detect package manager. Please install python3-tk manually."
    echo "For most distributions, one of these commands should work:"
    echo "  sudo apt-get install python3-tk    # Debian/Ubuntu"
    echo "  sudo dnf install python3-tkinter    # Fedora"
    echo "  sudo pacman -S tk                   # Arch"
    echo "  sudo zypper install python3-tk      # openSUSE"
fi

# Install Python packages from requirements.txt
echo "Installing Python packages..."
pip3 install -r requirements.txt

echo "Installation complete!"
echo "Run the application with: sudo python3 main.py"