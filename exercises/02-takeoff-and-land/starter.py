"""Exercise 02: take off to 5 m, hover for 10 seconds, then land.

Most of the work is in ../mydrone.py. This script just calls your functions in the right order.
Run it from the top folder of the repo:  python3 exercises/02-takeoff-and-land/starter.py
"""
import sys
from pathlib import Path

# Python looks for modules in the script's own folder. mydrone.py is one folder up,
# so add that folder to the list of places Python looks.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import mydrone  # noqa: E402  (this import has to come after the line above)

ALTITUDE = 5   # metres
HOVER = 10     # seconds

# TODO 1: connect to the drone with mydrone.connect() and store the result in `drone`
drone = None

# TODO 2: switch to GUIDED mode
print("Mode: GUIDED")

# TODO 3: arm the motors
print("Armed")

# TODO 4: take off to ALTITUDE

print(f"Reached {ALTITUDE} m. Hovering for {HOVER} s")
mydrone.wait(HOVER)

print("Landing")
# TODO 5: land, and wait until the drone has disarmed
print("Landed and disarmed")
