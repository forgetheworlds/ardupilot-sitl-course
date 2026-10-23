# 06 Fly in Webots

**Goal:** connect SITL to Webots, fly by hand, then run your stage 1 scripts in Webots without
changing them.

There is no code to write. This exercise is about understanding what changed and what didn't.

## What you need to know

Read [stage2-webots/README.md](../../stage2-webots/README.md) first, especially "How Webots and SITL
connect".

## Steps

1. Run `python3 check_setup.py --webots`. Fix anything that fails.
2. Follow "Connecting SITL to Webots" in the stage 2 README: open `iris.wbt`, then start SITL with
   `--model webots-python` and both parameter files.
3. Fly by hand in MAVProxy, like exercise 01: `mode GUIDED`, `arm throttle`, `takeoff 10`. Watch the
   drone in Webots. Then `mode LAND`.
4. Run your exercise 02 script. Then run exercise 03.
5. Start SITL again with `--out 127.0.0.1:14551` added, and record exercise 03 with exercise 04.
   Compare the plot with the one from stage 1.
6. Explore the world. In the scene tree, open `WorldInfo` and find `basicTimeStep`. Open the `Iris`
   node and find `controller` and `controllerArgs`.

## Hints

- If the console never says `Connected to ardupilot SITL`, check the SITL command. The model must be
  `webots-python`.
- If arming fails with a `PreArm` about gains, you forgot `iris-fixes.parm`, or you need `-w`.
- In Webots, drag with the left mouse button to turn the view, and scroll to zoom. The view follows
  the drone.

## What you should see

- The propellers spin up in Webots after `arm throttle`, and the drone climbs to 10 m.
- Your scripts work exactly as before. The messages and ports are the same.
- The stage 2 plot is a bit less smooth than stage 1. The Webots model has more realistic physics.

## Questions to think about

1. Your scripts didn't change at all. Why not? What part of the system changed?
2. Pause Webots with the pause button while the drone hovers. What happens in MAVProxy? Why doesn't
   the drone fall when you unpause? (Think about lockstep.)
3. What would happen if you set `basicTimeStep` to 32? (You can try it. Save a copy of the world
   first.)

## Try next

- Open `iris_camera.wbt` instead. It has a camera on the drone. ArduPilot's
  `libraries/SITL/examples/Webots_Python/scripts/example_camera_receive.py` shows the images.
- Copy `iris.wbt` to a new file in the same folder, and add some boxes with **Add** (`Ctrl+Shift+A`).
  Remember to add a `boundingObject` so the drone can hit them.
