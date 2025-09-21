# Clevo Fan Control GUI

A simple GUI application to monitor Clevo laptop fan speed and CPU temperature.

## Features
- Real-time CPU temperature monitoring
- Fan RPM display
- Fan duty cycle percentage
- Animated fan visualization that spins based on actual RPM
- Battery power consumption monitoring
- Service control for clevo-fancontrol and auto-cpufreq
- Power profile switching with RyzenAdj (Battery/AC modes)

## Requirements
- Python 3.6+
- tkinter (python3-tk)
- Pillow (PIL)
- sudo access (required by system tools)

## System Dependencies

The following tools need to be installed for full functionality:

### clevo-fancontrol
Fan control for Clevo laptops
- Repository: https://github.com/mmt050/clevo-fancontrol
- Required for: Fan speed monitoring and control
- Installation: Follow instructions in the repository

### auto-cpufreq
Automatic CPU speed & power optimizer for Linux
- Repository: https://github.com/AdnanHodzic/auto-cpufreq
- Required for: CPU frequency scaling and power management
- Installation:
  ```bash
  # Via snap
  sudo snap install auto-cpufreq

  # Or via git
  git clone https://github.com/AdnanHodzic/auto-cpufreq.git
  cd auto-cpufreq && sudo ./auto-cpufreq-installer
  ```

### RyzenAdj
Power management tool for AMD Ryzen processors
- Repository: https://github.com/FlyGoat/RyzenAdj
- Required for: Power limit adjustments (TDP control)
- Installation: Download from releases or build from source

## Installation

### Quick Install
```bash
chmod +x install.sh
./install.sh
```

### Manual Install

1. Install tkinter (varies by Linux distribution):
```bash
# Debian/Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# openSUSE
sudo zypper install python3-tk
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

Run the application with sudo (required for clevo-fancontrol):
```bash
sudo python3 main.py
```

## Testing

A test version is available that simulates sensor values:
```bash
python3 test_gui.py
```

## Files
- `main.py` - Main application
- `test_gui.py` - Test version with simulated values
- `fan.png` - Fan image (auto-generated if missing)
- `create_fan_image.py` - Standalone script to create fan image

## Troubleshooting

If you get a tkinter import error:
```bash
# Install tkinter for your Python version
sudo apt-get install python3-tk  # For Ubuntu/Debian
```

If clevo-fancontrol is not found:
- Ensure clevo-fancontrol is installed at `/usr/local/bin/clevo-fancontrol`
- Check that you have sudo privileges