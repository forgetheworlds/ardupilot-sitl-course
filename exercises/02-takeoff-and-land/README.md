# 02 Take off and land from Python

**Goal:** do what you did in exercise 01, from a Python script. The drone takes off to 5 m, hovers
for 10 seconds and lands.

## What you need to know

Read [exercises/README.md](../README.md) first, especially the `listen.py` walkthrough.

Your script talks to the drone through MAVProxy on UDP port 14550. Each thing you typed in
exercise 01 has a matching message:

| MAVProxy command | In Python |
| --- | --- |
| `mode GUIDED` | `drone.set_mode("GUIDED")` |
| `arm throttle` | `drone.arducopter_arm()` |
| `takeoff 5` | `MAV_CMD_NAV_TAKEOFF` sent with `command_long_send`, height in param7 |
| watching the height | reading `relative_alt` from `GLOBAL_POSITION_INT` |
| `mode LAND` | `drone.set_mode("LAND")` |

The catch is that sending a message doesn't mean it worked. The drone might refuse, or it might
take a while. Good drone code always **sends, then waits until it sees the result**. Each function
you write here follows that pattern.

## Steps

You write six functions in [mydrone.py](../mydrone.py) (the ones marked "exercise 02"), then use
them in [starter.py](starter.py). Do them in this order, and test as you go.

1. **`connect()`**. Copy the idea from `listen.py`. Fill in TODO 1 in `starter.py` and run it. You
   should see `Connected to system 1`. The other lines print too, but nothing happens yet, because
   those TODOs are still empty. Then add each call to `starter.py` as you write its function.
2. **`set_mode()`**. Ask for the mode, then loop: read a `HEARTBEAT`, and stop when
   `drone.flightmode` is the mode you asked for. Run the script again. The MAVProxy prompt should
   change to `GUIDED>`.
3. **`arm()`**. Same pattern: send, read a message, check, repeat. Print any `STATUSTEXT` so you can
   see `PreArm:` messages.
4. **`altitude()`** and **`takeoff()`**. Send the takeoff command, then wait for the height to get
   close to the target.
5. **`land()`**. Switch to `LAND` and wait until the motors are no longer armed.
6. Finish the `TODO`s in `starter.py` and run the whole thing.

Run it from the top folder of the repo while SITL is running:

```bash
python3 exercises/02-takeoff-and-land/starter.py
```

## Hints

- If the script hangs, add a `print()` inside your loop to see what it's waiting for.
- In `takeoff()`, wait for 95% of the target height. The drone often stops a few centimetres short.
- If the drone was already flying from a previous run, type `mode LAND` in MAVProxy and wait for it
  to disarm before you try again.
- `takeoff()` only works in `GUIDED` mode while armed. Check the order of your calls.

## What you should see

```
Connected to system 1
Mode: GUIDED
Armed
Reached 5 m. Hovering for 10 s
Landing
Landed and disarmed
```

On the SITL map the altitude goes up to about 5, stays there, and comes back to 0.

## Questions to think about

1. Why does `arm()` need a loop, instead of sending the arm command once?
2. What happens if you call `takeoff()` before `arm()`? Try it and read MAVProxy's output.
3. What would happen in `takeoff()` if you waited for exactly 5.0 m?

## Try next

- Print the height every time you read it in `takeoff()`, so you can watch it climb.
- After hovering, use `mydrone.move_to(drone, 10, 0, 5)` to fly 10 m north before landing.
