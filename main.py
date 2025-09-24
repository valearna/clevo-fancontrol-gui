import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import time
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("Please install Pillow: pip install Pillow")
    exit(1)
import math

# Path to your fan image
FAN_IMAGE = "fan.png"

# How often to refresh values (ms)
REFRESH_INTERVAL = 50  # 20 FPS for smooth animation

# Modern blue-focused color scheme
COLORS = {
    'bg_primary': '#0d1117',      # Deep blue-black background
    'bg_secondary': '#161b22',    # Blue-tinted secondary background
    'bg_tertiary': '#21262d',     # Blue-tinted cards
    'accent_blue': '#58a6ff',     # Bright blue accent
    'accent_blue_dark': '#1f6feb', # Darker blue for buttons
    'accent_green': '#3fb950',    # Success green with blue tint
    'accent_orange': '#f85149',   # Warning orange-red
    'accent_red': '#f85149',      # Error red
    'text_primary': '#f0f6fc',    # Primary text with blue tint
    'text_secondary': '#8b949e',  # Secondary text
    'border': '#30363d',          # Blue-tinted border
    'hover': '#30363d'            # Hover state
}

class FanMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pangolin 11 Fan Control")
        self.root.geometry("480x950")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.resizable(False, False)

        # Configure ttk style for modern appearance
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Load or create fan image
        if not os.path.exists(FAN_IMAGE):
            self.create_simple_fan_image()
        self.original_fan = Image.open(FAN_IMAGE)
        self.angle = 0
        self.last_update_time = time.time()

        self.create_ui()

    def configure_styles(self):
        """Configure modern ttk styles with better contrast and readability"""
        # Softer, more readable button colors
        button_colors = {
            'modern_bg': '#2d4a6b',        # Softer blue
            'modern_hover': '#3d5a7b',     # Slightly lighter blue
            'success_bg': '#1f5f3f',       # Softer green
            'success_hover': '#2f6f4f',    # Lighter green
            'warning_bg': '#7d3c2a',       # Softer orange-red
            'warning_hover': '#8d4c3a',    # Lighter orange-red
            'danger_bg': '#7d2a2a',        # Softer red
            'danger_hover': '#8d3a3a',     # Lighter red
        }

        # Configure button styles with better readability
        self.style.configure('Modern.TButton',
                           background=button_colors['modern_bg'],
                           foreground='#ffffff',
                           borderwidth=1,
                           relief='flat',
                           focuscolor='none',
                           font=('Segoe UI', 10))

        self.style.map('Modern.TButton',
                      background=[('active', button_colors['modern_hover']),
                                ('pressed', button_colors['modern_bg']),
                                ('disabled', COLORS['bg_secondary'])],
                      foreground=[('disabled', COLORS['text_secondary'])])

        self.style.configure('Success.TButton',
                           background=button_colors['success_bg'],
                           foreground='#ffffff',
                           borderwidth=1,
                           relief='flat',
                           focuscolor='none',
                           font=('Segoe UI', 10))

        self.style.map('Success.TButton',
                      background=[('active', button_colors['success_hover']),
                                ('pressed', button_colors['success_bg']),
                                ('disabled', COLORS['bg_secondary'])],
                      foreground=[('disabled', COLORS['text_secondary'])])

        self.style.configure('Warning.TButton',
                           background=button_colors['warning_bg'],
                           foreground='#ffffff',
                           borderwidth=1,
                           relief='flat',
                           focuscolor='none',
                           font=('Segoe UI', 10))

        self.style.map('Warning.TButton',
                      background=[('active', button_colors['warning_hover']),
                                ('pressed', button_colors['warning_bg']),
                                ('disabled', COLORS['bg_secondary'])],
                      foreground=[('disabled', COLORS['text_secondary'])])

        self.style.configure('Danger.TButton',
                           background=button_colors['danger_bg'],
                           foreground='#ffffff',
                           borderwidth=1,
                           relief='flat',
                           focuscolor='none',
                           font=('Segoe UI', 10))

        self.style.map('Danger.TButton',
                      background=[('active', button_colors['danger_hover']),
                                ('pressed', button_colors['danger_bg']),
                                ('disabled', COLORS['bg_secondary'])],
                      foreground=[('disabled', COLORS['text_secondary'])])

    def create_card_frame(self, parent, title=None):
        """Create a modern card-style frame"""
        card = tk.Frame(parent, bg=COLORS['bg_tertiary'], relief='flat', bd=1)
        card.pack(fill='x', padx=20, pady=8)

        if title:
            title_label = tk.Label(card, text=title,
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=COLORS['bg_tertiary'],
                                 fg=COLORS['text_primary'])
            title_label.pack(pady=(12, 8))

        return card

    def create_ui(self):
        """Create the main UI components"""
        # Main title
        title_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        title_frame.pack(fill='x', pady=(20, 10))

        title_label = tk.Label(title_frame, text="🌪️ Pangolin 11 Fan Control",
                             font=('Segoe UI', 16, 'bold'),
                             bg=COLORS['bg_primary'],
                             fg=COLORS['text_primary'])
        title_label.pack()

        # Fan visualization card
        fan_card = self.create_card_frame(self.root, "Fan Status")

        # Canvas for fan with modern styling - compact
        self.canvas = tk.Canvas(fan_card, width=120, height=120,
                              bg=COLORS['bg_secondary'],
                              highlightthickness=0)
        self.canvas.pack(padx=15, pady=(5, 5))
        self.fan_image = None

        # System metrics in the fan card - compact
        metrics_frame = tk.Frame(fan_card, bg=COLORS['bg_tertiary'])
        metrics_frame.pack(pady=(0, 10))

        self.label_temp = tk.Label(metrics_frame, font=("Segoe UI", 11),
                                 bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        self.label_temp.pack(pady=1)

        self.label_rpm = tk.Label(metrics_frame, font=("Segoe UI", 11),
                                bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        self.label_rpm.pack(pady=1)

        self.label_duty = tk.Label(metrics_frame, font=("Segoe UI", 11),
                                 bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        self.label_duty.pack(pady=1)

        # Power consumption card - compact
        power_card = self.create_card_frame(self.root, "⚡ Power Status")
        power_metrics = tk.Frame(power_card, bg=COLORS['bg_tertiary'])
        power_metrics.pack(pady=(0, 10))

        self.label_power = tk.Label(power_metrics, font=("Segoe UI", 11),
                                  bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        self.label_power.pack(pady=1)

        self.label_battery_status = tk.Label(power_metrics, font=("Segoe UI", 10),
                                           bg=COLORS['bg_tertiary'], fg=COLORS['text_secondary'])
        self.label_battery_status.pack(pady=1)

        # Clevo-fancontrol service card
        clevo_card = self.create_card_frame(self.root, "🔧 Clevo Fan Control Service")

        self.label_status = tk.Label(clevo_card, font=("Segoe UI", 11),
                                   bg=COLORS['bg_tertiary'])
        self.label_status.pack(pady=(0, 10))

        clevo_button_frame = tk.Frame(clevo_card, bg=COLORS['bg_tertiary'])
        clevo_button_frame.pack(pady=(0, 12))

        self.btn_start = ttk.Button(clevo_button_frame, text="▶ Start",
                                   command=self.start_service,
                                   style='Success.TButton',
                                   width=12)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = ttk.Button(clevo_button_frame, text="⏹ Stop",
                                  command=self.stop_service,
                                  style='Danger.TButton',
                                  width=12)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # Auto-cpufreq service card
        autocpufreq_card = self.create_card_frame(self.root, "⚙️ Auto-CPUFreq Service")

        self.label_autocpufreq_status = tk.Label(autocpufreq_card, font=("Segoe UI", 11),
                                               bg=COLORS['bg_tertiary'])
        self.label_autocpufreq_status.pack(pady=(0, 10))

        autocpufreq_button_frame = tk.Frame(autocpufreq_card, bg=COLORS['bg_tertiary'])
        autocpufreq_button_frame.pack(pady=(0, 12))

        self.btn_autocpufreq_start = ttk.Button(autocpufreq_button_frame, text="▶ Start",
                                               command=self.start_autocpufreq_service,
                                               style='Success.TButton',
                                               width=12)
        self.btn_autocpufreq_start.pack(side=tk.LEFT, padx=5)

        self.btn_autocpufreq_stop = ttk.Button(autocpufreq_button_frame, text="⏹ Stop",
                                              command=self.stop_autocpufreq_service,
                                              style='Danger.TButton',
                                              width=12)
        self.btn_autocpufreq_stop.pack(side=tk.LEFT, padx=5)

        # RyzenAdj power control card
        ryzenadj_card = self.create_card_frame(self.root, "🔋 RyzenAdj Power Control")

        self.label_ryzenadj_status = tk.Label(ryzenadj_card, font=("Segoe UI", 11),
                                            bg=COLORS['bg_tertiary'])
        self.label_ryzenadj_status.pack(pady=(0, 15))

        # Power mode buttons in a grid
        ryzenadj_button_container = tk.Frame(ryzenadj_card, bg=COLORS['bg_tertiary'])
        ryzenadj_button_container.pack(pady=(0, 12))

        # Top row with Battery and Quiet modes
        top_row = tk.Frame(ryzenadj_button_container, bg=COLORS['bg_tertiary'])
        top_row.pack(pady=5)

        self.btn_ryzenadj_battery = ttk.Button(top_row, text="🔋 Battery Mode\n12W/8W • 80°C",
                                              command=self.apply_battery_mode,
                                              style='Modern.TButton',
                                              width=18)
        self.btn_ryzenadj_battery.pack(side=tk.LEFT, padx=5)

        self.btn_ryzenadj_quiet = ttk.Button(top_row, text="🔇 Quiet Mode\n20W/15W • 90°C",
                                           command=self.apply_quiet_mode,
                                           style='Warning.TButton',
                                           width=18)
        self.btn_ryzenadj_quiet.pack(side=tk.LEFT, padx=5)

        # Bottom row with AC mode (centered)
        bottom_row = tk.Frame(ryzenadj_button_container, bg=COLORS['bg_tertiary'])
        bottom_row.pack(pady=5)

        self.btn_ryzenadj_ac = ttk.Button(bottom_row, text="⚡ Performance Mode\n30W/20W • 98°C",
                                         command=self.apply_ac_mode,
                                         style='Success.TButton',
                                         width=18)
        self.btn_ryzenadj_ac.pack()

        # Start updating
        self.update()
        self.update_service_status()
        self.update_autocpufreq_status()
        self.update_ryzenadj_status()

    def create_simple_fan_image(self, size=100, num_blades=7):
        """Create a simple fan image that blends with the blue UI theme"""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        center_x = size // 2
        center_y = size // 2
        radius = size // 2 - 8

        # Blue-tinted colors that blend with the UI
        outline_color = (88, 166, 255)     # accent_blue
        blade_color = (71, 135, 204)       # Darker blue
        center_color = (31, 111, 235)      # accent_blue_dark
        inner_center = (48, 54, 61)        # bg_tertiary

        # Draw outer circle with blue tint
        draw.ellipse([8, 8, size-8, size-8], outline=outline_color, width=3)

        # Draw center circle
        center_radius = size // 8
        draw.ellipse([center_x - center_radius, center_y - center_radius,
                      center_x + center_radius, center_y + center_radius],
                     fill=center_color)

        # Draw fan blades with blue tint
        for i in range(num_blades):
            angle = (2 * math.pi * i) / num_blades
            start_angle = math.degrees(angle) - 15
            end_angle = math.degrees(angle) + 15
            draw.pieslice([center_x - radius + 5, center_y - radius + 5,
                           center_x + radius - 5, center_y + radius - 5],
                          start=start_angle, end=end_angle,
                          fill=blade_color)

        # Draw smaller center circle
        inner_radius = size // 12
        draw.ellipse([center_x - inner_radius, center_y - inner_radius,
                      center_x + inner_radius, center_y + inner_radius],
                     fill=inner_center)

        img.save(FAN_IMAGE)

    def check_service_status(self):
        """Check if clevo-fancontrol service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "clevo-fancontrol"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "active"
        except Exception as e:
            print(f"Error checking service status: {e}")
            return False

    def check_autocpufreq_status(self):
        """Check if auto-cpufreq service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "auto-cpufreq"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "active"
        except Exception as e:
            print(f"Error checking auto-cpufreq status: {e}")
            return False

    def update_service_status(self):
        """Update service status label and button states"""
        is_running = self.check_service_status()
        if is_running:
            self.label_status.config(text="✅ Service Running", fg=COLORS['accent_green'])
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.label_status.config(text="❌ Service Stopped", fg=COLORS['accent_red'])
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def update_autocpufreq_status(self):
        """Update auto-cpufreq service status label and button states"""
        is_running = self.check_autocpufreq_status()
        if is_running:
            self.label_autocpufreq_status.config(text="✅ Service Running", fg=COLORS['accent_green'])
            self.btn_autocpufreq_start.config(state=tk.DISABLED)
            self.btn_autocpufreq_stop.config(state=tk.NORMAL)
        else:
            self.label_autocpufreq_status.config(text="❌ Service Stopped", fg=COLORS['accent_red'])
            self.btn_autocpufreq_start.config(state=tk.NORMAL)
            self.btn_autocpufreq_stop.config(state=tk.DISABLED)

    def start_service(self):
        """Start the clevo-fancontrol service"""
        try:
            result = subprocess.run(
                ["pkexec", "systemctl", "start", "clevo-fancontrol"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_service_status()
                tk.messagebox.showinfo("Success", "Service started successfully")
            else:
                tk.messagebox.showerror("Error", f"Failed to start service: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error starting service: {e}")

    def check_ryzenadj_status(self):
        """Check current ryzenadj power limits to determine mode"""
        try:
            result = subprocess.run(
                ["sudo", "ryzenadj", "--info"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                output = result.stdout
                import re

                # Extract STAPM and PPT limits
                stapm_match = re.search(r'STAPM LIMIT\s+\|\s+(\d+\.\d+)', output)
                fast_match = re.search(r'PPT LIMIT FAST\s+\|\s+(\d+\.\d+)', output)
                slow_match = re.search(r'PPT LIMIT SLOW\s+\|\s+(\d+\.\d+)', output)

                if stapm_match and fast_match and slow_match:
                    stapm = float(stapm_match.group(1))
                    fast = float(fast_match.group(1))
                    slow = float(slow_match.group(1))

                    # Battery mode: Fast ~12W, Slow ~8W
                    # Quiet mode: Fast ~20W, Slow ~15W
                    # AC mode: Fast ~30W, Slow ~20W
                    if fast <= 15 and slow <= 10:
                        return "battery", stapm, fast, slow
                    elif fast <= 22 and slow <= 17:
                        return "quiet", stapm, fast, slow
                    else:
                        return "ac", stapm, fast, slow

            return "unknown", 0, 0, 0
        except Exception as e:
            print(f"Error checking ryzenadj status: {e}")
            return "unknown", 0, 0, 0

    def update_ryzenadj_status(self):
        """Update ryzenadj status label and button states"""
        mode, stapm, fast, slow = self.check_ryzenadj_status()

        if mode == "battery":
            self.label_ryzenadj_status.config(
                text=f"🔋 Battery Mode Active • {fast:.0f}W/{slow:.0f}W",
                fg=COLORS['accent_blue']
            )
            self.btn_ryzenadj_battery.config(state=tk.DISABLED)
            self.btn_ryzenadj_quiet.config(state=tk.NORMAL)
            self.btn_ryzenadj_ac.config(state=tk.NORMAL)
        elif mode == "quiet":
            self.label_ryzenadj_status.config(
                text=f"🔇 Quiet Mode Active • {fast:.0f}W/{slow:.0f}W",
                fg=COLORS['accent_orange']
            )
            self.btn_ryzenadj_battery.config(state=tk.NORMAL)
            self.btn_ryzenadj_quiet.config(state=tk.DISABLED)
            self.btn_ryzenadj_ac.config(state=tk.NORMAL)
        elif mode == "ac":
            self.label_ryzenadj_status.config(
                text=f"⚡ Performance Mode Active • {fast:.0f}W/{slow:.0f}W",
                fg=COLORS['accent_green']
            )
            self.btn_ryzenadj_battery.config(state=tk.NORMAL)
            self.btn_ryzenadj_quiet.config(state=tk.NORMAL)
            self.btn_ryzenadj_ac.config(state=tk.DISABLED)
        else:
            self.label_ryzenadj_status.config(
                text="❓ Power Mode Unknown",
                fg=COLORS['text_secondary']
            )
            self.btn_ryzenadj_battery.config(state=tk.NORMAL)
            self.btn_ryzenadj_quiet.config(state=tk.NORMAL)
            self.btn_ryzenadj_ac.config(state=tk.NORMAL)

    def apply_battery_mode(self):
        """Apply battery/power-saving mode settings"""
        try:
            # Apply battery mode: slow-limit=8W, fast-limit=12W, tctl-temp=80°C
            result = subprocess.run(
                ["pkexec", "/usr/bin/ryzenadj", "--slow-limit=8000", "--fast-limit=12000", "--tctl-temp=80"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_ryzenadj_status()
                tk.messagebox.showinfo("Success", "Battery mode applied (12W fast, 8W slow, 80°C limit)")
            else:
                tk.messagebox.showerror("Error", f"Failed to apply battery mode: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error applying battery mode: {e}")

    def apply_quiet_mode(self):
        """Apply quiet mode settings - intermediate between battery and AC"""
        try:
            # Apply quiet mode: slow-limit=15W, fast-limit=20W, tctl-temp=90°C
            result = subprocess.run(
                ["pkexec", "/usr/bin/ryzenadj", "--slow-limit=15000", "--fast-limit=20000", "--tctl-temp=90"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_ryzenadj_status()
                tk.messagebox.showinfo("Success", "Quiet mode applied (20W fast, 15W slow, 90°C limit)")
            else:
                tk.messagebox.showerror("Error", f"Failed to apply quiet mode: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error applying quiet mode: {e}")

    def apply_ac_mode(self):
        """Reset to AC/default mode settings"""
        try:
            # Reset to default values: slow-limit=20W, fast-limit=30W, tctl-temp=98°C
            result = subprocess.run(
                ["pkexec", "/usr/bin/ryzenadj", "--slow-limit=20000", "--fast-limit=30000", "--tctl-temp=98"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_ryzenadj_status()
                tk.messagebox.showinfo("Success", "AC/Default mode restored (30W fast, 20W slow, 98°C limit)")
            else:
                tk.messagebox.showerror("Error", f"Failed to apply AC mode: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error applying AC mode: {e}")

    def stop_service(self):
        """Stop the clevo-fancontrol service"""
        try:
            result = subprocess.run(
                ["pkexec", "systemctl", "stop", "clevo-fancontrol"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_service_status()
                tk.messagebox.showinfo("Success", "Service stopped successfully")
            else:
                tk.messagebox.showerror("Error", f"Failed to stop service: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error stopping service: {e}")

    def start_autocpufreq_service(self):
        """Start the auto-cpufreq service"""
        try:
            result = subprocess.run(
                ["pkexec", "systemctl", "start", "auto-cpufreq"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_autocpufreq_status()
                tk.messagebox.showinfo("Success", "auto-cpufreq service started successfully")
            else:
                tk.messagebox.showerror("Error", f"Failed to start auto-cpufreq service: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error starting auto-cpufreq service: {e}")

    def stop_autocpufreq_service(self):
        """Stop the auto-cpufreq service"""
        try:
            result = subprocess.run(
                ["pkexec", "systemctl", "stop", "auto-cpufreq"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_autocpufreq_status()
                tk.messagebox.showinfo("Success", "auto-cpufreq service stopped successfully")
            else:
                tk.messagebox.showerror("Error", f"Failed to stop auto-cpufreq service: {result.stderr}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error stopping auto-cpufreq service: {e}")


    def get_battery_power(self):
        """Get battery power consumption in watts"""
        try:
            # Check if on battery or AC
            with open('/sys/class/power_supply/BAT0/status', 'r') as f:
                status = f.read().strip()

            # Read current in microamps
            try:
                with open('/sys/class/power_supply/BAT0/current_now', 'r') as f:
                    current_ua = int(f.read().strip())
            except:
                current_ua = 0

            # Read voltage in microvolts
            try:
                with open('/sys/class/power_supply/BAT0/voltage_now', 'r') as f:
                    voltage_uv = int(f.read().strip())
            except:
                voltage_uv = 0

            # Calculate power in watts (current in A * voltage in V)
            power_w = (current_ua / 1000000.0) * (voltage_uv / 1000000.0)

            return power_w, status
        except Exception as e:
            print(f"Error reading battery power: {e}")
            return 0, "Unknown"

    def get_sensor_values(self):
        """Run clevo-fancontrol and parse its output"""
        try:
            output = subprocess.check_output(
                ["sudo", "/usr/local/bin/clevo-fancontrol"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            # Remove wait_ec error lines that corrupt the JSON
            lines = output.split('\n')
            cleaned_lines = [line for line in lines if 'wait_ec error' not in line]
            cleaned_output = '\n'.join(cleaned_lines)

            try:
                data = json.loads(cleaned_output)
            except json.JSONDecodeError as je:
                # If still failing, try to extract values with regex as fallback
                import re
                duty_match = re.search(r'"duty":\s*(\d+)', output)
                rpms_match = re.search(r'"rpms":\s*(\d+)', output)
                temp_match = re.search(r'"cpu_temp_cels":\s*(\d+)', output)

                duty = int(duty_match.group(1)) if duty_match else 0
                rpms = int(rpms_match.group(1)) if rpms_match else 0
                temp = int(temp_match.group(1)) if temp_match else 0

                return temp, rpms, duty

            return data.get("cpu_temp_cels", 0), data.get("rpms", 0), data.get("duty", 0)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            return 0, 0, 0
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 0, 0, 0

    def update(self):
        temp, rpm, duty = self.get_sensor_values()

        power_w, battery_status = self.get_battery_power()

        # Update labels with modern styling
        self.label_temp.config(text=f"🌡️ CPU Temperature: {temp}°C")
        self.label_rpm.config(text=f"🌪️ Fan Speed: {rpm} RPM")
        self.label_duty.config(text=f"⚙️ Fan Duty: {duty}%")

        # Update power consumption labels with modern styling
        if battery_status == "Discharging":
            self.label_power.config(text=f"🔋 Battery Draw: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Status: {battery_status}", fg=COLORS['accent_orange'])
        elif battery_status == "Charging":
            self.label_power.config(text=f"🔌 Charging: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Status: {battery_status}", fg=COLORS['accent_green'])
        else:
            self.label_power.config(text=f"⚡ Power: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Status: {battery_status}", fg=COLORS['accent_blue'])

        # Clear canvas before redrawing
        self.canvas.delete("all")

        # Calculate time-based rotation with three discrete speeds
        current_time = time.time()
        time_delta = current_time - self.last_update_time
        self.last_update_time = current_time

        # Three-speed system to avoid visual artifacts
        # Stopped: 0 RPM
        # Slow: < 2000 RPM (visual speed: 120 degrees/second)
        # Fast: >= 2000 RPM (visual speed: 720 degrees/second)
        if rpm == 0:
            rotation_amount = 0
        elif rpm < 2000:
            # Slow speed - 120 degrees per second (20 RPM equivalent for visibility)
            rotation_amount = 120 * time_delta
        else:
            # Fast speed - 720 degrees per second (120 RPM equivalent for visibility)
            rotation_amount = 720 * time_delta

        self.angle = (self.angle + rotation_amount) % 360
        try:
            # Try newer PIL version first
            rotated = self.original_fan.rotate(-self.angle, resample=Image.Resampling.BICUBIC)
        except AttributeError:
            # Fall back to older PIL version
            rotated = self.original_fan.rotate(-self.angle, resample=Image.BICUBIC)
        self.fan_image = ImageTk.PhotoImage(rotated)
        self.canvas.create_image(60, 60, image=self.fan_image)

        # Update service status periodically (less frequently than sensor data)
        if not hasattr(self, 'status_counter'):
            self.status_counter = 0
        self.status_counter += 1
        if self.status_counter >= 20:  # Update every 20 refresh cycles (about 1 second)
            self.update_service_status()
            self.update_autocpufreq_status()
            self.update_ryzenadj_status()
            self.status_counter = 0

        # Schedule next update
        self.root.after(REFRESH_INTERVAL, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    app = FanMonitorApp(root)
    root.mainloop()
