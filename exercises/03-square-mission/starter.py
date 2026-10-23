"""Exercise 03: upload a square mission and fly it in AUTO mode.

Run it from the top folder of the repo:  python3 exercises/03-square-mission/starter.py
You need connect, set_mode, arm and takeoff from exercise 02 in ../mydrone.py.
"""
import math
import sys
from pathlib import Path

from pymavlink import mavutil

sys.path.append(str(Path(__file__).resolve().parent.parent))
import mydrone  # noqa: E402

SIDE = 20       # metres
ALTITUDE = 10   # metres
METRES_PER_DEGREE = 111_320


def square(side):
    """Return the corners of a square as a list of (north, east) pairs in metres from home.

    The last corner must be (0, 0), back at the start.
    """
    # TODO: return a list of four (north, east) tuples
    return []


def offset(lat, lon, north, east):
    """Return the (lat, lon) that is `north` and `east` metres away from (lat, lon)."""
    # TODO: work out new_lat and new_lon from the facts in the README
    new_lat = lat
    new_lon = lon
    return new_lat, new_lon


def mission_item(drone, seq, command, lat=0.0, lon=0.0, alt=0.0):
    """Build one mission item (but don't send it yet)."""
    return drone.mav.mission_item_int_encode(
        drone.target_system, drone.target_component,
        seq,                                                # item number
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # height is measured from home
        command,
        0,                  # current: 0 for an upload
        1,                  # autocontinue: go on to the next item when done
        0, 0, 0, 0,         # param1 to param4: not used by these commands
        int(lat * 1e7),     # latitude, degrees x 10^7 as a whole number
        int(lon * 1e7),     # longitude, the same
        alt)                # height in metres


def upload(drone, items):
    """Send a list of mission items to the drone, answering its requests one by one."""
    drone.mav.mission_count_send(drone.target_system, drone.target_component, len(items))
    while True:
        msg = drone.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT", "MISSION_ACK"],
                               blocking=True, timeout=5)
        if msg is None:
            raise RuntimeError("No reply from the drone during the upload")
        if msg.get_type() == "MISSION_ACK":
            break
        drone.mav.send(items[msg.seq])   # the drone asked for item number msg.seq
    print(f"Uploaded {len(items)} mission items")


drone = mydrone.connect()

# Home is where the drone is now. GLOBAL_POSITION_INT gives it in degrees x 10^7.
here = drone.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
home_lat, home_lon = here.lat / 1e7, here.lon / 1e7

nav = mavutil.mavlink
items = [
    mission_item(drone, 0, nav.MAV_CMD_NAV_WAYPOINT, home_lat, home_lon, 0),  # item 0: home
    mission_item(drone, 1, nav.MAV_CMD_NAV_TAKEOFF, alt=ALTITUDE),
]
for north, east in square(SIDE):
    lat, lon = offset(home_lat, home_lon, north, east)
    items.append(mission_item(drone, len(items), nav.MAV_CMD_NAV_WAYPOINT, lat, lon, ALTITUDE))
items.append(mission_item(drone, len(items), nav.MAV_CMD_NAV_RETURN_TO_LAUNCH))
upload(drone, items)

mydrone.set_mode(drone, "GUIDED")
mydrone.arm(drone)
mydrone.takeoff(drone, ALTITUDE)
mydrone.set_mode(drone, "AUTO")

# TODO: until the motors disarm, read MISSION_ITEM_REACHED and HEARTBEAT messages.
#       For each MISSION_ITEM_REACHED, print f"Reached item {msg.seq}".
#       (Reading HEARTBEAT too keeps drone.motors_armed() up to date.)

print("Landed and disarmed")
