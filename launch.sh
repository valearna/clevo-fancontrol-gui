#!/bin/bash
# Simple launcher for Pangolin 11 Power Control - runs without sudo, requests when needed

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the application directory
cd "$SCRIPT_DIR"

# Just run the app normally - it will handle sudo internally
exec /usr/bin/python3 main.py "$@"