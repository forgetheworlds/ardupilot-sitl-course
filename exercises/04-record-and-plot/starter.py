"""Exercise 04: record a flight, save it as CSV and plot it.

Start SITL with an extra output so this can run next to another script:
    sim_vehicle.py --console --map --out 127.0.0.1:14551
Then run this from the top folder of the repo, and fly something in another terminal:
    python3 exercises/04-record-and-plot/starter.py
"""
import csv
import math
import time

import matplotlib.pyplot as plt
from pymavlink import mavutil

COLUMNS = ["t", "north", "east", "up", "speed", "tilt"]


def record(address="udp:127.0.0.1:14551"):
    """Collect one row per position message until the drone lands. Return the list of rows."""
    drone = mavutil.mavlink_connection(address)
    drone.wait_heartbeat()
    print("Recording. Fly the drone. Recording stops when it lands (or press Ctrl+C).")

    rows = []
    sample = {}           # the latest value of each column
    start = time.time()
    was_armed = False     # becomes True once the drone has armed

    try:
        while True:
            msg = drone.recv_match(type=["LOCAL_POSITION_NED", "VFR_HUD", "ATTITUDE", "HEARTBEAT"],
                                   blocking=True, timeout=1)
            if msg is None:
                continue
            kind = msg.get_type()

            if kind == "HEARTBEAT":
                armed = drone.motors_armed()
                if was_armed and not armed:
                    break                       # it was flying and now it has landed
                if armed:
                    was_armed = True
            elif kind == "VFR_HUD":
                pass  # TODO: store the ground speed in sample["speed"]
            elif kind == "ATTITUDE":
                pass  # TODO: store the bigger of |roll| and |pitch|, in degrees, in sample["tilt"]
            elif kind == "LOCAL_POSITION_NED" and was_armed:
                # TODO: store the time since start (seconds) in sample["t"],
                #       and north, east and up (metres) in sample["north"], sample["east"], sample["up"]
                # TODO: then add a copy of sample to rows
                pass
    except KeyboardInterrupt:
        pass  # Ctrl+C stops the recording, then we save what we have

    # Drop rows from before the speed and tilt had arrived
    return [row for row in rows if all(column in row for column in COLUMNS)]


def save_csv(rows, path="flight.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} samples to {path}")


def plot(rows, path="flight.png"):
    t = [row["t"] for row in rows]   # a list of all the times, for the x axis
    fig, (top, height, speed) = plt.subplots(1, 3, figsize=(14, 4))

    # TODO 1: on `top`, plot east (x axis) against north (y axis): the path seen from above.
    #         Label the axes and use top.set_aspect("equal").
    # TODO 2: on `height`, plot up against t.
    # TODO 3: on `speed`, plot speed and tilt against t, each with a label=..., then add a legend.

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    print(f"Saved plot to {path}")


if __name__ == "__main__":
    rows = record()
    save_csv(rows)
    if rows:
        plot(rows)
