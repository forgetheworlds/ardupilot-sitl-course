"""Exercise 05: fly the same 40 m leg with two values of WP_SPD and compare.

Run it from the top folder of the repo:  python3 exercises/05-change-a-parameter/starter.py
You need set_param() in ../mydrone.py, plus the functions from exercise 02.
"""
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import mydrone  # noqa: E402

LEG = 40          # metres
ALTITUDE = 10     # metres
SPEEDS = [2, 8]   # values of WP_SPD to try, in m/s


def fly_leg(drone, north):
    """Fly to `north` metres north of home. Return (top speed in m/s, time taken in s)."""
    mydrone.move_to(drone, north, 0, ALTITUDE)
    start = None
    top_speed = 0.0
    while True:
        msg = drone.recv_match(type="LOCAL_POSITION_NED", blocking=True)
        if start is None:
            start = msg.time_boot_ms        # the drone's own clock, in milliseconds
        speed = math.hypot(msg.vx, msg.vy)  # horizontal speed in m/s
        # TODO: keep the highest speed seen so far in top_speed
        arrived = abs(msg.x - north) < 0.5 and speed < 0.3
        if arrived:
            return top_speed, (msg.time_boot_ms - start) / 1000


drone = mydrone.connect()
mydrone.set_mode(drone, "GUIDED")
mydrone.arm(drone)
mydrone.takeoff(drone, ALTITUDE)

results = []
for i, speed in enumerate(SPEEDS):          # enumerate gives the position (0, 1, ...) and the value
    # TODO: set WP_SPD to `speed` with mydrone.set_param()
    mydrone.set_mode(drone, "BRAKE")        # GUIDED reads WP_SPD when it starts,
    mydrone.set_mode(drone, "GUIDED")       # so leave GUIDED and come back
    target = LEG if i % 2 == 0 else 0       # fly out, then back
    top, seconds = fly_leg(drone, target)
    results.append((speed, top, seconds))

mydrone.land(drone)

print()
print("WP_SPD   top speed   time for 40 m")
for speed, top, seconds in results:
    print(f"{speed:2d} m/s    {top:4.1f} m/s      {seconds:5.1f} s")
