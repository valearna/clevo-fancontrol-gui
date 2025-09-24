import subprocess
import customtkinter as ctk
from tkinter import messagebox
import json
import os
import time
from collections import deque
import threading
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("Please install Pillow: pip install Pillow")
    exit(1)
import math
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from datetime import datetime

# Path to your fan image
FAN_IMAGE = "fan.png"

# How often to refresh values (ms)
REFRESH_INTERVAL = 1000  # 1 second for data updates
FAN_ANIMATION_INTERVAL = 50  # 50ms for smooth fan animation

# Set CustomTkinter appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FanMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pangolin 11 System Monitor")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 700)

        # Data storage for graphs (last 60 data points = 1 minute of history)
        self.temp_history = deque(maxlen=60)
        self.rpm_history = deque(maxlen=60)
        self.power_history = deque(maxlen=60)
        self.time_history = deque(maxlen=60)

        # Initialize with some data
        current_time = datetime.now()
        for i in range(60):
            self.temp_history.append(0)
            self.rpm_history.append(0)
            self.power_history.append(0)
            self.time_history.append((current_time.timestamp() - (60 - i)))

        # Load or create fan image
        if not os.path.exists(FAN_IMAGE):
            self.create_simple_fan_image()
        self.original_fan = Image.open(FAN_IMAGE)
        # Make fan smaller (80x80)
        try:
            self.original_fan = self.original_fan.resize((80, 80), Image.Resampling.LANCZOS)
        except AttributeError:
            self.original_fan = self.original_fan.resize((80, 80), Image.LANCZOS)
        self.fan_angle = 0
        self.last_fan_update = time.time()
        self.current_rpm = 0

        self.create_ui()
        self.start_updates()

    def create_simple_fan_image(self, size=100, num_blades=7):
        """Create a simple fan image with gradient effects"""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        center_x = size // 2
        center_y = size // 2
        radius = size // 2 - 8

        # Modern gradient-like colors
        outline_color = (41, 128, 185)     # Modern blue
        blade_color = (52, 152, 219)       # Lighter blue
        center_color = (41, 128, 185)      # Blue
        inner_center = (30, 30, 30)        # Dark center

        # Draw outer circle
        draw.ellipse([8, 8, size-8, size-8], outline=outline_color, width=2)

        # Draw fan blades
        for i in range(num_blades):
            angle = (2 * math.pi * i) / num_blades
            start_angle = math.degrees(angle) - 20
            end_angle = math.degrees(angle) + 20
            draw.pieslice([center_x - radius + 10, center_y - radius + 10,
                          center_x + radius - 10, center_y + radius - 10],
                         start=start_angle, end=end_angle,
                         fill=blade_color, outline=outline_color)

        # Draw center circles for depth
        center_radius = size // 6
        draw.ellipse([center_x - center_radius, center_y - center_radius,
                     center_x + center_radius, center_y + center_radius],
                    fill=center_color, outline=outline_color)

        inner_radius = size // 10
        draw.ellipse([center_x - inner_radius, center_y - inner_radius,
                     center_x + inner_radius, center_y + inner_radius],
                    fill=inner_center)

        img.save(FAN_IMAGE)

    def create_ui(self):
        """Create the modern UI with graphs"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title bar
        title_frame = ctk.CTkFrame(main_container, height=60, corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(title_frame,
                                  text="🚀 PANGOLIN 11 SYSTEM MONITOR",
                                  font=ctk.CTkFont(family="Courier New", size=20, weight="bold"))
        title_label.pack(pady=15)

        # Create two-column layout
        columns_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)

        # Left column (narrower)
        left_column = ctk.CTkFrame(columns_frame, width=400)
        left_column.pack(side="left", fill="both", padx=(0, 10))
        left_column.pack_propagate(False)

        # Right column (wider for graphs)
        right_column = ctk.CTkFrame(columns_frame, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True)

        # === LEFT COLUMN CONTENT ===

        # System Status Card
        status_card = self.create_card(left_column, "💻 System Status", height=220)

        # Fan animation with smaller size
        fan_frame = ctk.CTkFrame(status_card, fg_color="transparent", height=80)
        fan_frame.pack(pady=(5, 5))

        self.fan_canvas = ctk.CTkCanvas(fan_frame, width=80, height=80,
                                       bg="#212121", highlightthickness=0)
        self.fan_canvas.pack()

        # Live metrics with modern styling
        metrics_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        metrics_frame.pack(pady=5, fill="x", padx=20)

        self.temp_label = ctk.CTkLabel(metrics_frame, text="CPU: --°C",
                                      font=ctk.CTkFont(family="Courier New", size=14, weight="bold"))
        self.temp_label.pack(pady=1)

        self.rpm_label = ctk.CTkLabel(metrics_frame, text="FAN: ---- RPM",
                                     font=ctk.CTkFont(family="Courier New", size=14, weight="bold"))
        self.rpm_label.pack(pady=1)

        self.power_label = ctk.CTkLabel(metrics_frame, text="POWER: --.-- W",
                                       font=ctk.CTkFont(family="Courier New", size=14, weight="bold"))
        self.power_label.pack(pady=1)

        self.battery_label = ctk.CTkLabel(metrics_frame, text="STATUS: Unknown",
                                        font=ctk.CTkFont(family="Courier New", size=12))
        self.battery_label.pack(pady=1)

        # Services Control Card
        services_card = self.create_card(left_column, "⚙️ Services Control", height=260)

        # Clevo service
        clevo_frame = ctk.CTkFrame(services_card, fg_color="transparent")
        clevo_frame.pack(pady=10, fill="x", padx=20)

        self.clevo_status = ctk.CTkLabel(clevo_frame, text="Clevo Fan Control: Unknown",
                                        font=ctk.CTkFont(family="Courier New", size=14))
        self.clevo_status.pack(pady=5)

        clevo_buttons = ctk.CTkFrame(clevo_frame, fg_color="transparent")
        clevo_buttons.pack(pady=5)

        self.clevo_start = ctk.CTkButton(clevo_buttons, text="Start", width=80,
                                        command=self.start_clevo_service,
                                        fg_color="#2d5a2d", hover_color="#3d7a3d")
        self.clevo_start.pack(side="left", padx=5)

        self.clevo_stop = ctk.CTkButton(clevo_buttons, text="Stop", width=80,
                                       command=self.stop_clevo_service,
                                       fg_color="#5a2d2d", hover_color="#7a3d3d")
        self.clevo_stop.pack(side="left", padx=5)

        # Auto-CPUFreq service
        cpufreq_frame = ctk.CTkFrame(services_card, fg_color="transparent")
        cpufreq_frame.pack(pady=10, fill="x", padx=20)

        self.cpufreq_status = ctk.CTkLabel(cpufreq_frame, text="Auto-CPUFreq: Unknown",
                                          font=ctk.CTkFont(family="Courier New", size=14))
        self.cpufreq_status.pack(pady=5)

        cpufreq_buttons = ctk.CTkFrame(cpufreq_frame, fg_color="transparent")
        cpufreq_buttons.pack(pady=5)

        self.cpufreq_start = ctk.CTkButton(cpufreq_buttons, text="Start", width=80,
                                          command=self.start_cpufreq_service,
                                          fg_color="#2d5a2d", hover_color="#3d7a3d")
        self.cpufreq_start.pack(side="left", padx=5)

        self.cpufreq_stop = ctk.CTkButton(cpufreq_buttons, text="Stop", width=80,
                                         command=self.stop_cpufreq_service,
                                         fg_color="#5a2d2d", hover_color="#7a3d3d")
        self.cpufreq_stop.pack(side="left", padx=5)

        # Power Profiles Card
        power_card = self.create_card(left_column, "🔋 Power Profiles")

        self.ryzenadj_status = ctk.CTkLabel(power_card, text="Current Profile: Unknown",
                                           font=ctk.CTkFont(family="Courier New", size=14, weight="bold"))
        self.ryzenadj_status.pack(pady=10)

        profiles_frame = ctk.CTkFrame(power_card, fg_color="transparent")
        profiles_frame.pack(pady=10, fill="x", padx=20)

        # Profile buttons with icons
        self.battery_btn = ctk.CTkButton(profiles_frame, text="🔋 Battery\n12W/8W",
                                        width=100, height=60,
                                        command=self.apply_battery_mode,
                                        fg_color="#2d4a5a", hover_color="#3d5a6a")
        self.battery_btn.pack(side="left", padx=5)

        self.quiet_btn = ctk.CTkButton(profiles_frame, text="🔇 Quiet\n20W/15W",
                                      width=100, height=60,
                                      command=self.apply_quiet_mode,
                                      fg_color="#5a4a2d", hover_color="#6a5a3d")
        self.quiet_btn.pack(side="left", padx=5)

        self.perf_btn = ctk.CTkButton(profiles_frame, text="⚡ Performance\n30W/20W",
                                     width=100, height=60,
                                     command=self.apply_ac_mode,
                                     fg_color="#2d5a2d", hover_color="#3d7a3d")
        self.perf_btn.pack(side="left", padx=5)

        # === RIGHT COLUMN CONTENT (GRAPHS) ===

        # Temperature Graph
        temp_graph_card = self.create_card(right_column, "🌡️ Temperature History", height=240)
        self.create_temp_graph(temp_graph_card)

        # Fan Speed Graph
        fan_graph_card = self.create_card(right_column, "💨 Fan Speed History", height=240)
        self.create_fan_graph(fan_graph_card)

        # Power Consumption Graph
        power_graph_card = self.create_card(right_column, "⚡ Power Consumption", height=240)
        self.create_power_graph(power_graph_card)

    def create_card(self, parent, title, height=None):
        """Create a modern card widget"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        if height:
            card.configure(height=height)
            card.pack(fill="x", pady=(0, 15))
            card.pack_propagate(False)
        else:
            card.pack(fill="x", pady=(0, 15))

        if title:
            title_label = ctk.CTkLabel(card, text=title,
                                      font=ctk.CTkFont(family="Courier New", size=16, weight="bold"))
            title_label.pack(pady=(15, 5))

        return card

    def create_temp_graph(self, parent):
        """Create temperature graph"""
        fig = Figure(figsize=(6, 2), dpi=80, facecolor='#212121')
        self.temp_ax = fig.add_subplot(111)
        self.temp_ax.set_facecolor('#1a1a1a')
        self.temp_ax.set_ylabel('Temperature (°C)', color='white', fontsize=9)
        self.temp_ax.tick_params(colors='white', labelsize=8)
        self.temp_ax.grid(True, alpha=0.2, color='white')
        self.temp_ax.spines['bottom'].set_color('white')
        self.temp_ax.spines['top'].set_color('#1a1a1a')
        self.temp_ax.spines['left'].set_color('white')
        self.temp_ax.spines['right'].set_color('#1a1a1a')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.temp_canvas = canvas

    def create_fan_graph(self, parent):
        """Create fan speed graph"""
        fig = Figure(figsize=(6, 2), dpi=80, facecolor='#212121')
        self.fan_ax = fig.add_subplot(111)
        self.fan_ax.set_facecolor('#1a1a1a')
        self.fan_ax.set_ylabel('Fan Speed (RPM)', color='white', fontsize=9)
        self.fan_ax.tick_params(colors='white', labelsize=8)
        self.fan_ax.grid(True, alpha=0.2, color='white')
        self.fan_ax.spines['bottom'].set_color('white')
        self.fan_ax.spines['top'].set_color('#1a1a1a')
        self.fan_ax.spines['left'].set_color('white')
        self.fan_ax.spines['right'].set_color('#1a1a1a')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.fan_speed_canvas = canvas

    def create_power_graph(self, parent):
        """Create power consumption graph"""
        fig = Figure(figsize=(6, 2), dpi=80, facecolor='#212121')
        self.power_ax = fig.add_subplot(111)
        self.power_ax.set_facecolor('#1a1a1a')
        self.power_ax.set_ylabel('Power (W)', color='white', fontsize=9)
        self.power_ax.set_xlabel('Time (seconds ago)', color='white', fontsize=9)
        self.power_ax.tick_params(colors='white', labelsize=8)
        self.power_ax.grid(True, alpha=0.2, color='white')
        self.power_ax.spines['bottom'].set_color('white')
        self.power_ax.spines['top'].set_color('#1a1a1a')
        self.power_ax.spines['left'].set_color('white')
        self.power_ax.spines['right'].set_color('#1a1a1a')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.power_canvas = canvas

    def update_graphs(self):
        """Update all graphs with latest data"""
        x_values = list(range(60, 0, -1))  # 60 to 1 seconds ago

        # Update temperature graph
        self.temp_ax.clear()
        self.temp_ax.plot(x_values, list(self.temp_history), color='#ff6b6b', linewidth=2)
        self.temp_ax.fill_between(x_values, list(self.temp_history), alpha=0.3, color='#ff6b6b')
        self.temp_ax.set_ylabel('Temperature (°C)', color='white', fontsize=9)
        self.temp_ax.set_ylim(0, max(100, max(self.temp_history) + 10) if self.temp_history else 100)
        self.temp_ax.grid(True, alpha=0.2, color='white')
        self.temp_ax.set_facecolor('#1a1a1a')
        self.temp_ax.tick_params(colors='white', labelsize=8)
        self.temp_canvas.draw()

        # Update fan speed graph
        self.fan_ax.clear()
        self.fan_ax.plot(x_values, list(self.rpm_history), color='#4ecdc4', linewidth=2)
        self.fan_ax.fill_between(x_values, list(self.rpm_history), alpha=0.3, color='#4ecdc4')
        self.fan_ax.set_ylabel('Fan Speed (RPM)', color='white', fontsize=9)
        self.fan_ax.set_ylim(0, max(5000, max(self.rpm_history) + 500) if self.rpm_history else 5000)
        self.fan_ax.grid(True, alpha=0.2, color='white')
        self.fan_ax.set_facecolor('#1a1a1a')
        self.fan_ax.tick_params(colors='white', labelsize=8)
        self.fan_speed_canvas.draw()

        # Update power graph
        self.power_ax.clear()
        self.power_ax.plot(x_values, list(self.power_history), color='#f7b731', linewidth=2)
        self.power_ax.fill_between(x_values, list(self.power_history), alpha=0.3, color='#f7b731')
        self.power_ax.set_ylabel('Power (W)', color='white', fontsize=9)
        self.power_ax.set_xlabel('Time (seconds ago)', color='white', fontsize=9)
        self.power_ax.set_ylim(0, max(50, max(self.power_history) + 5) if self.power_history else 50)
        self.power_ax.grid(True, alpha=0.2, color='white')
        self.power_ax.set_facecolor('#1a1a1a')
        self.power_ax.tick_params(colors='white', labelsize=8)
        self.power_canvas.draw()

    def get_sensor_values(self):
        """Get sensor values from clevo-fancontrol"""
        try:
            output = subprocess.check_output(
                ["sudo", "/usr/local/bin/clevo-fancontrol"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            lines = output.split('\n')
            cleaned_lines = [line for line in lines if 'wait_ec error' not in line]
            cleaned_output = '\n'.join(cleaned_lines)

            try:
                data = json.loads(cleaned_output)
            except json.JSONDecodeError:
                import re
                duty_match = re.search(r'"duty":\s*(\d+)', output)
                rpms_match = re.search(r'"rpms":\s*(\d+)', output)
                temp_match = re.search(r'"cpu_temp_cels":\s*(\d+)', output)

                duty = int(duty_match.group(1)) if duty_match else 0
                rpms = int(rpms_match.group(1)) if rpms_match else 0
                temp = int(temp_match.group(1)) if temp_match else 0

                return temp, rpms, duty

            return data.get("cpu_temp_cels", 0), data.get("rpms", 0), data.get("duty", 0)
        except:
            return 0, 0, 0

    def get_battery_power(self):
        """Get battery power consumption"""
        try:
            with open('/sys/class/power_supply/BAT0/status', 'r') as f:
                status = f.read().strip()

            try:
                with open('/sys/class/power_supply/BAT0/current_now', 'r') as f:
                    current_ua = int(f.read().strip())
            except:
                current_ua = 0

            try:
                with open('/sys/class/power_supply/BAT0/voltage_now', 'r') as f:
                    voltage_uv = int(f.read().strip())
            except:
                voltage_uv = 0

            power_w = (current_ua / 1000000.0) * (voltage_uv / 1000000.0)
            return power_w, status
        except:
            return 0, "Unknown"

    def update_data(self):
        """Update sensor data and graphs"""
        temp, rpm, duty = self.get_sensor_values()
        power_w, battery_status = self.get_battery_power()

        # Store current rpm for fan animation
        self.current_rpm = rpm

        # Update history
        self.temp_history.append(temp)
        self.rpm_history.append(rpm)
        self.power_history.append(power_w)
        self.time_history.append(datetime.now().timestamp())

        # Update labels with colors based on values
        temp_color = "#ff6b6b" if temp > 80 else "#f7b731" if temp > 60 else "#74c0fc"
        self.temp_label.configure(text=f"CPU: {temp}°C", text_color=temp_color)

        rpm_color = "#ff6b6b" if rpm > 4000 else "#f7b731" if rpm > 2000 else "#a78bfa"
        self.rpm_label.configure(text=f"FAN: {rpm} RPM ({duty}%)", text_color=rpm_color)

        power_color = "#ff6b6b" if power_w > 30 else "#f7b731" if power_w > 20 else "#22d3ee"
        self.power_label.configure(text=f"POWER: {power_w:.2f} W", text_color=power_color)

        status_icons = {"Discharging": "🔋", "Charging": "⚡", "Full": "✅"}
        icon = status_icons.get(battery_status, "❓")
        self.battery_label.configure(text=f"STATUS: {icon} {battery_status}")

        # Update graphs
        self.update_graphs()

        # Update service statuses
        self.update_service_statuses()

        # Schedule next update
        self.root.after(REFRESH_INTERVAL, self.update_data)

    def animate_fan(self):
        """Animate the fan based on RPM"""
        current_time = time.time()
        time_delta = current_time - self.last_fan_update
        self.last_fan_update = current_time

        # Calculate rotation speed based on RPM
        if self.current_rpm == 0:
            rotation_speed = 0
        elif self.current_rpm < 2000:
            rotation_speed = 180  # degrees per second
        else:
            rotation_speed = 360 + (self.current_rpm / 5000) * 360  # Faster for higher RPM

        self.fan_angle = (self.fan_angle + rotation_speed * time_delta) % 360

        # Clear and redraw
        self.fan_canvas.delete("all")

        # Rotate fan image
        try:
            rotated = self.original_fan.rotate(-self.fan_angle, resample=Image.Resampling.BICUBIC)
        except AttributeError:
            rotated = self.original_fan.rotate(-self.fan_angle, resample=Image.BICUBIC)
        self.fan_image = ImageTk.PhotoImage(rotated)
        self.fan_canvas.create_image(40, 40, image=self.fan_image)

        # Schedule next animation frame
        self.root.after(FAN_ANIMATION_INTERVAL, self.animate_fan)

    def update_service_statuses(self):
        """Update all service statuses"""
        # Check Clevo service
        try:
            result = subprocess.run(["systemctl", "is-active", "clevo-fancontrol"],
                                 capture_output=True, text=True)
            clevo_active = result.stdout.strip() == "active"
            if clevo_active:
                self.clevo_status.configure(text="Clevo Fan Control: ✅ Running",
                                          text_color="#74c0fc")
                self.clevo_start.configure(state="disabled")
                self.clevo_stop.configure(state="normal")
            else:
                self.clevo_status.configure(text="Clevo Fan Control: ❌ Stopped",
                                          text_color="#ff6b6b")
                self.clevo_start.configure(state="normal")
                self.clevo_stop.configure(state="disabled")
        except:
            pass

        # Check Auto-CPUFreq service
        try:
            result = subprocess.run(["systemctl", "is-active", "auto-cpufreq"],
                                 capture_output=True, text=True)
            cpufreq_active = result.stdout.strip() == "active"
            if cpufreq_active:
                self.cpufreq_status.configure(text="Auto-CPUFreq: ✅ Running",
                                            text_color="#74c0fc")
                self.cpufreq_start.configure(state="disabled")
                self.cpufreq_stop.configure(state="normal")
            else:
                self.cpufreq_status.configure(text="Auto-CPUFreq: ❌ Stopped",
                                            text_color="#ff6b6b")
                self.cpufreq_start.configure(state="normal")
                self.cpufreq_stop.configure(state="disabled")
        except:
            pass

        # Check RyzenAdj profile
        try:
            result = subprocess.run(["sudo", "ryzenadj", "--info"],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                import re
                fast_match = re.search(r'PPT LIMIT FAST\s+\|\s+(\d+\.\d+)', result.stdout)
                slow_match = re.search(r'PPT LIMIT SLOW\s+\|\s+(\d+\.\d+)', result.stdout)

                if fast_match and slow_match:
                    fast = float(fast_match.group(1))
                    slow = float(slow_match.group(1))

                    if fast <= 15:
                        profile = "🔋 Battery Mode"
                        self.battery_btn.configure(state="disabled")
                        self.quiet_btn.configure(state="normal")
                        self.perf_btn.configure(state="normal")
                    elif fast <= 22:
                        profile = "🔇 Quiet Mode"
                        self.battery_btn.configure(state="normal")
                        self.quiet_btn.configure(state="disabled")
                        self.perf_btn.configure(state="normal")
                    else:
                        profile = "⚡ Performance Mode"
                        self.battery_btn.configure(state="normal")
                        self.quiet_btn.configure(state="normal")
                        self.perf_btn.configure(state="disabled")

                    self.ryzenadj_status.configure(
                        text=f"Current Profile: {profile}\n({fast:.0f}W/{slow:.0f}W)")
        except:
            pass

    def start_updates(self):
        """Start all update loops"""
        self.update_data()
        self.animate_fan()

    # Service control methods
    def start_clevo_service(self):
        try:
            subprocess.run(["pkexec", "systemctl", "start", "clevo-fancontrol"])
            messagebox.showinfo("Success", "Clevo service started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start service: {e}")

    def stop_clevo_service(self):
        try:
            subprocess.run(["pkexec", "systemctl", "stop", "clevo-fancontrol"])
            messagebox.showinfo("Success", "Clevo service stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop service: {e}")

    def start_cpufreq_service(self):
        try:
            subprocess.run(["pkexec", "systemctl", "start", "auto-cpufreq"])
            messagebox.showinfo("Success", "Auto-CPUFreq service started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start service: {e}")

    def stop_cpufreq_service(self):
        try:
            subprocess.run(["pkexec", "systemctl", "stop", "auto-cpufreq"])
            messagebox.showinfo("Success", "Auto-CPUFreq service stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop service: {e}")

    def apply_battery_mode(self):
        try:
            subprocess.run(["pkexec", "/usr/bin/ryzenadj", "--slow-limit=8000",
                          "--fast-limit=12000", "--tctl-temp=80"])
            messagebox.showinfo("Success", "Battery mode applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply mode: {e}")

    def apply_quiet_mode(self):
        try:
            subprocess.run(["pkexec", "/usr/bin/ryzenadj", "--slow-limit=15000",
                          "--fast-limit=20000", "--tctl-temp=90"])
            messagebox.showinfo("Success", "Quiet mode applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply mode: {e}")

    def apply_ac_mode(self):
        try:
            subprocess.run(["pkexec", "/usr/bin/ryzenadj", "--slow-limit=20000",
                          "--fast-limit=30000", "--tctl-temp=98"])
            messagebox.showinfo("Success", "Performance mode applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply mode: {e}")


if __name__ == "__main__":
    app = ctk.CTk()
    monitor = FanMonitorApp(app)
    app.mainloop()