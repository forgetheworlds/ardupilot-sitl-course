# Stage 1: ArduPilot SITL

In this stage you fly ArduPilot's built-in simulator. Nothing else is needed. Before you start, make
sure `python3 check_setup.py` passes.

## What runs when you start SITL

When you run `sim_vehicle.py`, three programs start:

```
 arducopter (SITL)  <--- TCP 5760 --->  MAVProxy  ---> UDP 14550 --->  your Python script
  autopilot code                        ground station                 (pymavlink)
  + simple physics
```

1. **`arducopter`** is the autopilot. It is the same C++ code that runs on a flight controller.
   Instead of reading real sensors, it reads a simple physics model built into SITL.
2. **MAVProxy** connects to SITL over TCP port 5760. It gives you the `STABILIZE>` prompt, the
   console window and the map.
3. MAVProxy also forwards every message to **UDP port 14550**. Your scripts listen there. Anything
   your script sends to 14550 goes back through MAVProxy to the autopilot.

So you can type commands in MAVProxy and run a script at the same time. Both talk to the same drone.

## Start SITL

```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map
```

Wait until the console shows `EKF3 IMU0 is using GPS`. EKF is the part of the autopilot that works
out where the drone is. Until it has a GPS position, the drone refuses to arm.

Useful options (run `sim_vehicle.py -h` for all of them):

| Option | What it does |
| --- | --- |
| `-w` | wipe saved parameters and start fresh |
| `--console --map` | open the console and map windows |
| `--out 127.0.0.1:14551` | send a second copy of the messages to port 14551 (exercise 04 uses this) |
| `-L CMAC` | start at a named location (the list is in `Tools/autotest/locations.txt`) |
| `--speedup 2` | run the simulation twice as fast |

## MAVProxy basics

You type commands at the prompt. The prompt shows the current flight mode, for example
`GUIDED>`.

| Command | What it does |
| --- | --- |
| `mode GUIDED` | change flight mode |
| `arm throttle` | start the motors |
| `disarm` | stop the motors (only safe on the ground) |
| `takeoff 10` | climb to 10 m (needs `GUIDED` and armed) |
| `status` | print the latest copy of every message |
| `param show WP_SPD` | show a parameter |
| `param set WP_SPD 3` | change a parameter |
| `wp list` | show the uploaded mission |

On the map you can right-click and pick **Fly To** while in `GUIDED` mode.

Read the [MAVProxy cheatsheet](https://ardupilot.org/mavproxy/docs/getting_started/cheatsheet.html)
once. You don't need to remember it.

## Flight modes you will use

A flight mode decides who is in control and how. Read
[Copter flight modes](https://ardupilot.org/copter/docs/flight-modes.html) for the full list.

| Mode | What the drone does |
| --- | --- |
| `STABILIZE` | a pilot flies it with sticks. SITL starts in this mode |
| `GUIDED` | it follows commands from a ground station or a script |
| `AUTO` | it flies the uploaded mission on its own |
| `LAND` | it lands where it is, then disarms |
| `RTL` | it flies back to where it armed and lands |
| `BRAKE` | it stops as fast as it can and holds still |

## Exercises

1. [01 First flight](../exercises/01-first-flight): fly with MAVProxy commands only.
2. Read [exercises/README.md](../exercises/README.md). It explains the Python you will need.
3. [02 Take off and land from Python](../exercises/02-takeoff-and-land)
4. [03 Fly a square mission](../exercises/03-square-mission)
5. [04 Record and plot a flight](../exercises/04-record-and-plot)
6. [05 Change a parameter](../exercises/05-change-a-parameter)

## When something goes wrong

- **`PreArm: ...` when you arm.** Read the rest of the message. Right after starting, it's usually
  still waiting for GPS. Wait 30 seconds and try again.
- **The drone is somewhere strange, or a parameter you changed is still changed.** Start again with
  `-w`.
- **Your script waits forever at "Waiting for heartbeat".** SITL isn't running, or your script is
  listening on the wrong port. MAVProxy prints the ports it forwards to when it starts.
- **Commands are ignored.** Check the flight mode. Most commands only work in `GUIDED`.
