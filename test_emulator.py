#!/usr/bin/env python3
import os
import sys
import logging

# Set emulator mode before any imports
os.environ["EMULATOR"] = "true"

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d - %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

print("Starting LEDMatrix Emulator with Basketball Plugin...")
print(f"EMULATOR mode: {os.environ.get('EMULATOR', 'false')}")

# Now import the display controller
from src.display_controller import main

if __name__ == "__main__":
    main()
