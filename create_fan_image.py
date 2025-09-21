#!/usr/bin/env python3
from PIL import Image, ImageDraw
import math

def create_fan_image(size=150, num_blades=7):
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

        # Blade start and end angles
        start_angle = math.degrees(angle) - 15
        end_angle = math.degrees(angle) + 15

        # Draw blade as pie slice
        draw.pieslice([center_x - radius + 5, center_y - radius + 5,
                       center_x + radius - 5, center_y + radius - 5],
                      start=start_angle, end=end_angle,
                      fill=(80, 80, 80))

    # Draw smaller center circle
    inner_radius = size // 12
    draw.ellipse([center_x - inner_radius, center_y - inner_radius,
                  center_x + inner_radius, center_y + inner_radius],
                 fill=(60, 60, 60))

    img.save('fan.png')
    print("Fan image created: fan.png")

if __name__ == "__main__":
    create_fan_image()