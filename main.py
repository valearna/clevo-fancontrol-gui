import subprocess
import tkinter as tk
from tkinter import messagebox
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

class FanMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pangolin 11 fan control")
        self.root.geometry("450x720")

        # Load or create fan image
        if not os.path.exists(FAN_IMAGE):
            self.create_simple_fan_image()
        self.original_fan = Image.open(FAN_IMAGE)
        self.angle = 0
        self.last_update_time = time.time()

        # Canvas for fan
        self.canvas = tk.Canvas(root, width=200, height=200, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.fan_image = None

        # Labels
        self.label_temp = tk.Label(root, font=("Arial", 14))
        self.label_temp.pack()
        self.label_rpm = tk.Label(root, font=("Arial", 14))
        self.label_rpm.pack()
        self.label_duty = tk.Label(root, font=("Arial", 14))
        self.label_duty.pack()

        # Power consumption labels
        self.label_power = tk.Label(root, font=("Arial", 14))
        self.label_power.pack()
        self.label_battery_status = tk.Label(root, font=("Arial", 12))
        self.label_battery_status.pack()

        # Separator for clevo-fancontrol section
        separator1 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        separator1.pack(fill=tk.X, padx=5, pady=10)

        # Clevo-fancontrol section title
        self.label_clevo_title = tk.Label(root, text="clevo-fancontrol Service", font=("Arial", 12, "bold"))
        self.label_clevo_title.pack(pady=5)

        # Service status label
        self.label_status = tk.Label(root, font=("Arial", 12), fg="green")
        self.label_status.pack(pady=5)

        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Start/Stop buttons
        self.btn_start = tk.Button(button_frame, text="Start Service",
                                   command=self.start_service,
                                   font=("Arial", 10),
                                   padx=10, pady=5)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(button_frame, text="Stop Service",
                                  command=self.stop_service,
                                  font=("Arial", 10),
                                  padx=10, pady=5)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # Separator for auto-cpufreq section
        separator2 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        separator2.pack(fill=tk.X, padx=5, pady=10)

        # Auto-cpufreq section title
        self.label_autocpufreq_title = tk.Label(root, text="auto-cpufreq Service", font=("Arial", 12, "bold"))
        self.label_autocpufreq_title.pack(pady=5)

        # Auto-cpufreq status label
        self.label_autocpufreq_status = tk.Label(root, font=("Arial", 12), fg="green")
        self.label_autocpufreq_status.pack(pady=5)

        # Auto-cpufreq button frame
        autocpufreq_frame = tk.Frame(root)
        autocpufreq_frame.pack(pady=10)

        # Start/Stop buttons for auto-cpufreq
        self.btn_autocpufreq_start = tk.Button(autocpufreq_frame, text="Start Service",
                                               command=self.start_autocpufreq_service,
                                               font=("Arial", 10),
                                               padx=10, pady=5)
        self.btn_autocpufreq_start.pack(side=tk.LEFT, padx=5)

        self.btn_autocpufreq_stop = tk.Button(autocpufreq_frame, text="Stop Service",
                                              command=self.stop_autocpufreq_service,
                                              font=("Arial", 10),
                                              padx=10, pady=5)
        self.btn_autocpufreq_stop.pack(side=tk.LEFT, padx=5)

        # Separator for RyzenAdj section
        separator3 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        separator3.pack(fill=tk.X, padx=5, pady=10)

        # RyzenAdj section
        self.label_ryzenadj_title = tk.Label(root, text="RyzenAdj Power Control", font=("Arial", 12, "bold"))
        self.label_ryzenadj_title.pack(pady=5)

        # RyzenAdj status label
        self.label_ryzenadj_status = tk.Label(root, font=("Arial", 11))
        self.label_ryzenadj_status.pack(pady=5)

        # RyzenAdj button frame
        ryzenadj_frame = tk.Frame(root)
        ryzenadj_frame.pack(pady=5)

        # Battery/Power-saving mode button
        self.btn_ryzenadj_battery = tk.Button(ryzenadj_frame, text="Battery Mode\n(12W/8W, 80°C)",
                                              command=self.apply_battery_mode,
                                              font=("Arial", 10),
                                              width=15,
                                              padx=15, pady=10)
        self.btn_ryzenadj_battery.pack(side=tk.LEFT, padx=5)

        # AC/Performance mode button
        self.btn_ryzenadj_ac = tk.Button(ryzenadj_frame, text="AC Mode\n(Default)",
                                         command=self.apply_ac_mode,
                                         font=("Arial", 10),
                                         width=15,
                                         padx=15, pady=10)
        self.btn_ryzenadj_ac.pack(side=tk.LEFT, padx=5)

        # Start updating
        self.update()
        self.update_service_status()
        self.update_autocpufreq_status()
        self.update_ryzenadj_status()

    def create_simple_fan_image(self, size=150, num_blades=7):
        """Create a simple fan image if none exists"""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        center_x = size // 2
        center_y = size // 2
        radius = size // 2 - 10

        # Draw outer circle
        draw.ellipse([10, 10, size-10, size-10], outline=(50, 50, 50), width=3)

        # Draw center circle
        center_radius = size // 8
        draw.ellipse([center_x - center_radius, center_y - center_radius,
                      center_x + center_radius, center_y + center_radius],
                     fill=(100, 100, 100))

        # Draw fan blades
        for i in range(num_blades):
            angle = (2 * math.pi * i) / num_blades
            start_angle = math.degrees(angle) - 15
            end_angle = math.degrees(angle) + 15
            draw.pieslice([center_x - radius + 5, center_y - radius + 5,
                           center_x + radius - 5, center_y + radius - 5],
                          start=start_angle, end=end_angle,
                          fill=(80, 80, 80))

        # Draw smaller center circle
        inner_radius = size // 12
        draw.ellipse([center_x - inner_radius, center_y - inner_radius,
                      center_x + inner_radius, center_y + inner_radius],
                     fill=(60, 60, 60))

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
            self.label_status.config(text="Status: Running", fg="green")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.label_status.config(text="Status: Stopped", fg="red")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def update_autocpufreq_status(self):
        """Update auto-cpufreq service status label and button states"""
        is_running = self.check_autocpufreq_status()
        if is_running:
            self.label_autocpufreq_status.config(text="Status: Running", fg="green")
            self.btn_autocpufreq_start.config(state=tk.DISABLED)
            self.btn_autocpufreq_stop.config(state=tk.NORMAL)
        else:
            self.label_autocpufreq_status.config(text="Status: Stopped", fg="red")
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

                    # Battery mode: STAPM ~10W, Fast ~12W, Slow ~8W
                    # AC mode: STAPM ~29W, Fast ~30W, Slow ~20W
                    if stapm <= 15 and fast <= 15 and slow <= 10:
                        return "battery", stapm, fast, slow
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
                text=f"Battery Mode: {fast:.0f}W/{slow:.0f}W",
                fg="blue"
            )
            self.btn_ryzenadj_battery.config(state=tk.DISABLED)
            self.btn_ryzenadj_ac.config(state=tk.NORMAL)
        elif mode == "ac":
            self.label_ryzenadj_status.config(
                text=f"AC Mode: {fast:.0f}W/{slow:.0f}W",
                fg="green"
            )
            self.btn_ryzenadj_battery.config(state=tk.NORMAL)
            self.btn_ryzenadj_ac.config(state=tk.DISABLED)
        else:
            self.label_ryzenadj_status.config(
                text="Mode: Unknown",
                fg="gray"
            )
            self.btn_ryzenadj_battery.config(state=tk.NORMAL)
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

                # Sanity checks for obviously wrong values
                if temp > 150:  # 224°C is clearly wrong
                    temp = 0
                if rpms > 10000:  # Most laptop fans max out around 5000-6000 RPM
                    rpms = 0

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

        # Update labels
        self.label_temp.config(text=f"CPU Temp: {temp} °C")
        self.label_rpm.config(text=f"Fan Speed: {rpm} RPM")
        self.label_duty.config(text=f"Fan Duty: {duty}%")

        # Update power consumption labels
        if battery_status == "Discharging":
            self.label_power.config(text=f"Power Draw: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Battery: {battery_status}", fg="orange")
        elif battery_status == "Charging":
            self.label_power.config(text=f"Charging: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Battery: {battery_status}", fg="green")
        else:
            self.label_power.config(text=f"Power: {power_w:.2f} W")
            self.label_battery_status.config(text=f"Battery: {battery_status}", fg="blue")

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
        self.canvas.create_image(100, 100, image=self.fan_image)

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
