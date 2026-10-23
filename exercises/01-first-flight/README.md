# 01 First flight

**Goal:** take off to 10 m, fly somewhere on the map, come back and land. Use only MAVProxy commands.
No code yet.

## What you need to know

- **Arming** turns the motors on. The autopilot runs safety checks first, called pre-arm checks. If
  one fails, it refuses and prints `PreArm:` and the reason.
- **Flight modes** decide who is in control. SITL starts in `STABILIZE`, which needs a pilot with
  sticks. `GUIDED` lets a ground station give orders, so you switch to it before taking off.
- **Home** is where the drone was when it armed. `RTL` (return to launch) flies back there.

Read the "MAVProxy basics" and "Flight modes" parts of [stage1-sitl/README.md](../../stage1-sitl/README.md).

## Steps

1. Start SITL:
   ```bash
   cd ~/ardupilot/ArduCopter
   sim_vehicle.py --console --map
   ```
2. Wait for `EKF3 IMU0 is using GPS` in the console.
3. Open [commands.txt](commands.txt). Fill in the blanks using the tables in the stage 1 README.
4. Type the commands into the MAVProxy prompt one at a time. Wait for each one to finish before
   typing the next one. Watch the console and the map.
5. While the drone hovers, right-click on the map, pick **Fly To**, and enter the height. Watch it
   fly there.
6. Bring it home with `RTL`, and watch it land and disarm.

## Hints

- If `arm throttle` fails, read the `PreArm:` message. Most often the drone is still waiting for GPS.
- If `takeoff` does nothing, check the prompt. Are you in `GUIDED`? Are the motors armed?
- If you wait more than about 10 seconds after arming without taking off, the drone disarms itself.
  That's a safety feature. Arm again.

## What you should see

- MAVProxy prints `ARMED`, then `Got COMMAND_ACK: NAV_TAKEOFF: ACCEPTED`.
- The console's altitude rises to about 10 and stays there.
- The drone icon moves on the map and leaves a trail.
- After `RTL` it flies back, comes down, and MAVProxy prints `DISARMED`.

## Questions to think about

1. Type `status GLOBAL_POSITION_INT` while hovering. Which field is the height, and what unit is
   it in?
2. What does the drone do if you type `mode LAND` while it flies to a point? How is that different
   from `mode RTL`?
3. Try `mode BRAKE` while it moves. What happens?

## Try next

- Change how fast it climbs in `GUIDED`: `param set WP_SPD_UP 5` (m/s), then take off again.
- Start SITL at a different place with `-L`. The list of places is in
  `~/ardupilot/Tools/autotest/locations.txt`.
