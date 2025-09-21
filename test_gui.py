#!/usr/bin/env python3
import subprocess
import tkinter as tk
import json
import os
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("Please install Pillow: pip install Pillow")
    exit(1)
import math
import random

# Path to your fan image
FAN_IMAGE = "fan.png"

# How often to refresh values (ms)
REFRESH_INTERVAL = 1000

class FanMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clevo Fan Monitor (Test Mode)")
        self.root.geometry("300x350")

        # Load or create fan image
        if not os.path.exists(FAN_IMAGE):
            self.create_simple_fan_image()
        self.original_fan = Image.open(FAN_IMAGE)
        self.angle = 0

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

        # Test mode indicator
        self.label_mode = tk.Label(root, text="TEST MODE", font=("Arial", 10), fg="red")
        self.label_mode.pack()

        # Start updating
        self.update()

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

    def get_sensor_values(self):
        """Simulate sensor values for testing"""
        # Generate random but realistic values
        temp = random.randint(40, 75)
        duty = random.randint(0, 100)
        # RPM based on duty cycle
        if duty == 0:
            rpm = 0
        else:
            rpm = int(duty * 30 + random.randint(-200, 200))
            rpm = max(0, min(rpm, 4000))

        return temp, rpm, duty

    def update(self):
        temp, rpm, duty = self.get_sensor_values()

        # Update labels
        self.label_temp.config(text=f"CPU Temp: {temp} °C")
        self.label_rpm.config(text=f"Fan Speed: {rpm} RPM")
        self.label_duty.config(text=f"Fan Duty: {duty}%")

        # Clear canvas before redrawing
        self.canvas.delete("all")

        # Spin fan based on RPM (max RPM around 4000-5000)
        if rpm > 0:
            speed_factor = min(rpm / 500.0, 20)  # Limit max speed
        else:
            speed_factor = 0

        self.angle = (self.angle + speed_factor) % 360
        try:
            # Try newer PIL version first
            rotated = self.original_fan.rotate(-self.angle, resample=Image.Resampling.BICUBIC)
        except AttributeError:
            # Fall back to older PIL version
            rotated = self.original_fan.rotate(-self.angle, resample=Image.BICUBIC)
        self.fan_image = ImageTk.PhotoImage(rotated)
        self.canvas.create_image(100, 100, image=self.fan_image)

        # Schedule next update
        self.root.after(REFRESH_INTERVAL, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    app = FanMonitorApp(root)
    root.mainloop()