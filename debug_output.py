#!/usr/bin/env python3
import subprocess

try:
    output = subprocess.check_output(
        ["sudo", "/usr/local/bin/clevo-fancontrol"],
        text=True,
        stderr=subprocess.STDOUT
    )
    print("Raw output:")
    print(repr(output))
    print("\nFormatted output:")
    print(output)
    print("\nBytes in output:")
    for i, char in enumerate(output):
        print(f"  Position {i}: '{char}' (ASCII {ord(char)})")
except Exception as e:
    print(f"Error: {e}")