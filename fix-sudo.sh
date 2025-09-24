#!/bin/bash
# Fix script for sudo authentication in Pang11 Fan Control

echo "This script will fix the sudo authentication for Pang11 Fan Control"
echo "You'll need to enter your password when prompted."
echo ""

# Update the desktop file to use pkexec directly
echo "Updating desktop file to use pkexec..."
sudo tee /usr/share/applications/pang11-fancontrol.desktop > /dev/null << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Pangolin 11 Power Control
Comment=Comprehensive power management for Pangolin 11 laptop
Icon=pang11-fancontrol
Exec=pkexec /opt/pang11-fancontrol-gui/launch.sh
Terminal=false
Categories=System;Settings;HardwareSettings;
Keywords=fan;temperature;cpu;cooling;pang11;pangolin;laptop;power;ryzen;frequency;
StartupNotify=true
StartupWMClass=Pang11-FanControl
EOF

# Update the wrapper to be simpler
echo "Updating wrapper script..."
sudo tee /usr/local/bin/pang11-fancontrol-gui > /dev/null << 'EOF'
#!/bin/bash
# Simple wrapper - the desktop file handles pkexec
exec /opt/pang11-fancontrol-gui/launch.sh "$@"
EOF

sudo chmod +x /usr/local/bin/pang11-fancontrol-gui

# Create a polkit policy to allow running with GUI
echo "Creating polkit policy..."
sudo tee /usr/share/polkit-1/actions/com.pang11.fancontrol.policy > /dev/null << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <vendor>Pang11 Fan Control</vendor>
  <vendor_url>https://github.com/pang11-fancontrol-gui</vendor_url>

  <action id="com.pang11.fancontrol.run">
    <description>Run Pang11 Fan Control GUI</description>
    <message>Authentication is required to run Pang11 Fan Control with hardware access</message>
    <icon_name>pang11-fancontrol</icon_name>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/opt/pang11-fancontrol-gui/launch.sh</annotate>
    <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
  </action>
</policyconfig>
EOF

# Update desktop database
echo "Updating desktop database..."
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "Done! The application will now:"
echo "1. Show a password prompt when launched from the menu"
echo "2. Run with full sudo access to read sensor data"
echo ""
echo "Please log out and back in, or restart your desktop shell."