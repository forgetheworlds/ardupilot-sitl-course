"""Example script: connect to the drone and print its flight mode and height for 10 seconds.

Run it while SITL is running:  python3 exercises/listen.py
exercises/README.md explains it line by line.
"""
import time

from pymavlink import mavutil

drone = mavutil.mavlink_connection("udp:127.0.0.1:14550")
print("Waiting for heartbeat...")
drone.wait_heartbeat()
print(f"Connected to system {drone.target_system}")

end = time.time() + 10
while time.time() < end:
    msg = drone.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)
    if msg is None:
        print("No position message yet")
        continue
    height = msg.relative_alt / 1000
    print(f"Mode: {drone.flightmode}   height: {height:.1f} m")
