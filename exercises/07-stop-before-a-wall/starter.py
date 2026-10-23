"""Exercise 07: fly towards a wall and stop before it, using the depth camera.

Open obstacle.wbt in Webots and start SITL first (see the README).
Run it from the top folder of the repo:  python3 exercises/07-stop-before-a-wall/starter.py
"""
import socket
import struct
import sys
import threading
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))
import mydrone  # noqa: E402

ALTITUDE = 2          # metres
SPEED = 1.5           # m/s
STOP_DISTANCE = 5.0   # metres
MAX_RANGE = 20.0      # must match maxRange of the RangeFinder in obstacle.wbt

# The thread writes the latest distance here, and the main code reads it.
latest = {"distance": MAX_RANGE}


def read_depth_camera(port=5599):
    """Keep latest["distance"] updated with the distance straight ahead, in metres."""
    sock = socket.create_connection(("127.0.0.1", port))
    while True:
        # Each image starts with its width and height: two 16-bit numbers, 4 bytes in total.
        width, height = struct.unpack("=HH", sock.recv(4, socket.MSG_WAITALL))
        # Then one byte per pixel. Turn the bytes into a 2D array of distances in metres.
        pixels = np.frombuffer(sock.recv(width * height, socket.MSG_WAITALL), np.uint8)
        image = pixels.reshape(height, width) / 255 * MAX_RANGE

        # TODO: take the middle third of the image (rows and columns),
        #       and store its median in latest["distance"]


# Start the reader in the background. daemon=True means it stops when the script ends.
threading.Thread(target=read_depth_camera, daemon=True).start()

drone = mydrone.connect()
mydrone.set_mode(drone, "GUIDED")
mydrone.arm(drone)
mydrone.takeoff(drone, ALTITUDE)

print("Flying forward")
while True:  # TODO: keep going only while the wall is farther than STOP_DISTANCE
    mydrone.move_forward(drone, SPEED)
    print(f"  wall ahead: {latest['distance']:4.1f} m")
    mydrone.wait(0.2)

print(f"Wall at {latest['distance']:.1f} m. Stopping.")
mydrone.set_mode(drone, "BRAKE")
mydrone.wait(3)
print(f"Holding at {latest['distance']:.1f} m from the wall")
mydrone.land(drone)
print("Landed and disarmed")
