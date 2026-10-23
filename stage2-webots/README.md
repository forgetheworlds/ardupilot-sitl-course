# Stage 2: Webots

In stage 1, SITL used its own simple physics. In this stage, Webots takes over the physics. You get a
3D view, a real-looking world, and sensors like cameras. The autopilot and your scripts stay the
same.

Before you start, run `python3 check_setup.py --webots`. Read Webots'
[Tutorial 1: Your first simulation](https://cyberbotics.com/doc/guide/tutorial-1-your-first-simulation-in-webots)
and ArduPilot's [Using SITL with Webots Python](https://ardupilot.org/dev/docs/sitl-with-webots-python.html).

## How Webots works

### Worlds

A **world** is a `.wbt` file. It describes everything in the simulation: the ground, the sky, the
lights, objects and robots. It's plain text, so you can open it in an editor. When you open a world
in Webots, it shows it in 3D and starts the simulation.

### Nodes and the scene tree

Everything in a world is a **node**. A node has a type and some fields. For example, the wall in this
course's obstacle world is a `Solid` node:

```
Solid {
  translation 15 0 2      # 15 m in front of the start, 2 m up
  children [
    Shape {
      geometry DEF WALL Box { size 0.5 8 4 }
    }
  ]
  boundingObject USE WALL  # the shape used for collisions
}
```

Nodes can hold other nodes in `children`. Webots shows this nesting on the left of the window as the
**scene tree**. Click any node there to see and change its fields. Read
[The scene tree](https://cyberbotics.com/doc/guide/the-scene-tree).

A few node types matter here:

- `WorldInfo` holds settings for the whole world, including `basicTimeStep` (see below).
- `Solid` is a physical object. `boundingObject` is the shape used for collisions, and
  `physics` gives it a mass. Without `physics`, it stays fixed in place, like the wall.
- `Robot` is a solid that runs a program, called a controller. Devices like `Motor`, `GPS`, `Gyro`,
  `Accelerometer`, `InertialUnit` and `RangeFinder` go inside a robot.

### PROTOs

A **PROTO** is a reusable node, made from other nodes. Think of it like a Python function that
builds a piece of the world. The Iris drone is a PROTO, in
`libraries/SITL/examples/Webots_Python/protos/Iris.proto`. A world loads it with:

```
EXTERNPROTO "../protos/Iris.proto"
```

and then uses it as if it were a built-in node: `Iris { ... }`. The path is relative to the world
file. That's why the course's world must sit in ArduPilot's `worlds` folder.

`Iris` has an `extensionSlot` field. Whatever you put there is mounted on the drone. That's how the
obstacle world adds a depth camera.

### Controllers

A **controller** is the program that runs a robot. It is a normal Python (or C) program. In a loop,
it reads the robot's sensors and sets its motors. The robot's `controller` field names the
controller, and Webots looks for it in the `controllers` folder next to `worlds`.

Every Iris uses the controller `ardupilot_vehicle_controller`. `controllerArgs` passes it options,
like command-line arguments: the motor names, and which camera to stream.

### The simulation step

Webots doesn't run continuously. It moves time forward in small, fixed steps. Each step, it works out
the physics: forces from the motors, gravity, drag, collisions. The size of the step is
`basicTimeStep` in `WorldInfo`, in milliseconds.

The ArduPilot worlds use `basicTimeStep 2`, so 500 physics steps per simulated second. ArduPilot's
docs say to keep it at 1 or 2. A bigger step means the autopilot gets sensor data too rarely to fly
well.

A controller moves time forward by calling `robot.step(timestep)`. Until it does, the simulation
waits for it.

Webots can run at real-time speed, or faster if your computer can manage it. The toolbar buttons
choose. If your computer is too slow to keep up, simulated time runs slower than real time. The
"Real time factor" is shown at the top of the 3D view.

## How Webots and SITL connect

```
 Webots                                       ArduPilot SITL
 ┌───────────────────────────┐   sensors     ┌──────────────────┐
 │ Iris robot                │ ────────────> │ arducopter       │
 │ ardupilot_vehicle_        │   UDP 9003    │ --model          │
 │ controller.py             │               │   webots-python  │
 │                           │ <──────────── │                  │
 └───────────────────────────┘   motors      └──────────────────┘
                                 UDP 9002            │ MAVLink
                                                     v
                                          MAVProxy -> UDP 14550 -> your script
```

1. When the world starts, the controller opens UDP port 9002 and prints
   `Listening for ardupilot SITL`. Webots is now waiting.
2. You start SITL with `--model webots-python`. Instead of its own physics, SITL now sends motor
   commands to port 9002.
3. Each time the controller gets motor commands, it sets the four motor speeds. Then it steps the
   simulation once and sends back a sensor packet to port 9003: time, gyro, accelerometer,
   orientation, velocity and position.
4. SITL runs the autopilot code with those sensor readings and sends the next motor commands.

The packets are small blocks of binary numbers: 16 floats for the motors, and 16 doubles for the
sensors. They're defined near the top of
`libraries/SITL/examples/Webots_Python/controllers/ardupilot_vehicle_controller/webots_vehicle.py`.
Read its `_handle_sitl` function. It's short, and it's the whole connection.

Webots also uses a different axis convention from ArduPilot. The controller flips the signs of some
axes before sending, so ArduPilot gets north-east-down, as on a real drone.

### Lockstep

The two programs take turns. Webots doesn't step until it gets motor commands, and SITL doesn't run
the next loop until it gets sensors. This is called **lockstep**. It means neither side can get ahead
of the other. If your computer is slow, the whole simulation slows down together, instead of the
drone falling out of the sky.

There's one limit. ArduPilot checks how often its gyro gives new readings. If the simulation is very
slow, the gyro looks too slow and the drone won't arm (`PreArm: Gyro rate < loop rate`). That's one
reason for the parameter file below.

### Physics

Webots computes the physics with ODE, an open-source physics engine. The Iris PROTO sets the drone's
mass and inertia, and each propeller's thrust and drag constants. The controller just tells each
motor how fast to spin. Webots turns that into thrust and torque, and the drone moves.

This is closer to reality than SITL's built-in model, but it's still a model. A real drone has wind,
vibration, sensor noise and battery sag. Don't assume tuning from the simulator will be perfect on a
real drone.

## Connecting SITL to Webots

1. Open Webots. Use **File > Open World** and pick
   `~/ardupilot/libraries/SITL/examples/Webots_Python/worlds/iris.wbt`. The time counter starts and
   the console says `Listening for ardupilot SITL (I0) at 127.0.0.1:9002`.
2. In a terminal, start SITL with the Webots model:
   ```bash
   cd ~/ardupilot
   Tools/autotest/sim_vehicle.py -v ArduCopter -w --model webots-python \
     --add-param-file=libraries/SITL/examples/Webots_Python/params/iris.parm \
     --add-param-file=/path/to/this/repo/stage2-webots/iris-fixes.parm \
     --console --map
   ```
3. The Webots console says `Connected to ardupilot SITL`. Wait for `EKF3 IMU0 is using GPS` in
   MAVProxy, about 30 seconds.

`iris.parm` comes with ArduPilot. It sets up the autopilot for the Webots Iris: frame type, tuning,
and a few simulation shortcuts.

[iris-fixes.parm](iris-fixes.parm) is from this course. It's needed on Copter 4.7, because the
stock `iris.parm` was written for older versions. Without it, the drone refuses to arm. Open it and
read the comments: it sets a small non-zero rate I-gain, turns off two acro settings that 4.7
checks, and lowers the loop rate so slower computers can keep up.

> **Note:** always start Webots first, then SITL. If you restart one of them, restart both.

> **Windows (WSL2):** if you installed Webots on the Windows side instead of in Ubuntu, add
> `--sim-address=<Windows IP>` to the SITL command, as the ArduPilot page explains.

## Exercises

1. [06 Fly in Webots](../exercises/06-fly-in-webots)
2. [07 Stop before a wall](../exercises/07-stop-before-a-wall)

## When something goes wrong

- **Nothing moves in Webots, and the console never says `Connected`.** SITL isn't sending to the
  right place. Check you used `--model webots-python`. If Webots runs on Windows and SITL in WSL2,
  you need `--sim-address`.
- **`PreArm` messages about gains or `ACRO_BAL`.** You forgot `iris-fixes.parm`. Restart SITL with it,
  and with `-w` so old values are wiped.
- **`PreArm: Gyro rate < loop rate`, or the drone flips on takeoff.** The simulation is too slow.
  Make the Webots window smaller, close other programs, and check the real time factor.
- **The world has no sky or ground textures.** Webots downloads them the first time. Check your
  internet connection, then reload with `Ctrl+Shift+R`.
- **Port already in use.** An old SITL or Webots is still running. Close it, or find it with
  `ps aux | grep -e arducopter -e webots`.
