# Python and pymavlink for the exercises

This page explains all the Python and pymavlink syntax the exercises use. It assumes you know basic
Python: variables, `if`, `for` loops and functions. If those are new, do sections 3 and 4 of the
[Python tutorial](https://docs.python.org/3/tutorial/) first.

Read it once from top to bottom. Then keep it open while you work.

## How the exercises work

Each exercise folder has:

- `README.md`: the goal, the ideas you need, the steps, hints, and what you should see.
- `starter.py`: a skeleton. The parts you write are marked `TODO`. Comments explain the rest.

Some exercises also ask you to fill in functions in [mydrone.py](mydrone.py). These are small helpers
(connect, arm, take off, land) that you write once in exercise 02 and reuse after that.

Run a script from the top folder of this repo, while SITL is running in another terminal:

```bash
python3 exercises/02-takeoff-and-land/starter.py
```

Stop a script at any time with `Ctrl+C`. If the drone is still flying, type `mode LAND` in MAVProxy.

## A short example, line by line

[listen.py](listen.py) connects to the drone and prints its mode and height for 10 seconds. Start
SITL, then run it:

```bash
python3 exercises/listen.py
```

You should see something like:

```
Waiting for heartbeat...
Connected to system 1
Mode: STABILIZE   height: 0.0 m
Mode: STABILIZE   height: 0.0 m
...
```

Here is the script:

```python
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
```

`import time` loads Python's built-in `time` module. You use `time.time()` (the current time in
seconds) and `time.sleep()` from it.

`from pymavlink import mavutil` loads the `mavutil` part of pymavlink. It has the function that
opens a connection, and the list of every MAVLink constant.

`drone = mavutil.mavlink_connection("udp:127.0.0.1:14550")` opens a connection and stores it in
`drone`. The text says how to connect: listen for UDP messages on your own computer
(`127.0.0.1`), port `14550`. That's where MAVProxy forwards messages. `drone` is an object, which
means it holds data (like `drone.target_system`) and has functions you call with a dot (like
`drone.wait_heartbeat()`).

`drone.wait_heartbeat()` waits until a `HEARTBEAT` message arrives. The autopilot sends one every
second to say it's alive. Your script must wait for one before sending anything. It's how pymavlink
learns which system to talk to.

`print(f"Connected to system {drone.target_system}")` is an f-string. The `f` before the quotes lets
you put a value in `{}` inside the text. `drone.target_system` is the ID of the autopilot that sent
the heartbeat, usually `1`.

`end = time.time() + 10` works out the time 10 seconds from now.

`while time.time() < end:` repeats the indented block as long as the condition is true. Here that
means "for 10 seconds".

`msg = drone.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)` waits for the next
message of one type. More on this below. If no message arrives within 2 seconds, it gives back
`None`.

`if msg is None:` checks for that case. `continue` jumps back to the top of the loop and skips the
rest of the block.

`height = msg.relative_alt / 1000` reads one field of the message. `relative_alt` is the height
above the take-off point, in millimetres, so you divide by 1000 to get metres.

`{height:.1f}` prints the number with one digit after the decimal point. `drone.flightmode` is the
current flight mode as text. pymavlink updates it each time a heartbeat arrives.

## Python you will see

### Functions

```python
def takeoff(drone, altitude):
    """Climb to `altitude` metres."""
    ...
```

`def` makes a function. `drone` and `altitude` are its inputs. The text in triple quotes is a
docstring. It says what the function does. In the skeletons, a function body may be
`raise NotImplementedError(...)`. Delete that line and write your code instead.

A function can give back a value with `return`, or several values at once:

```python
def position(drone):
    msg = drone.recv_match(type="LOCAL_POSITION_NED", blocking=True)
    return msg.x, msg.y, -msg.z

north, east, up = position(drone)   # unpack the three values
```

### Loops that wait for something

Most drone code waits for something to happen. There are two common ways to write it.

Loop while a condition is true:

```python
while drone.motors_armed():         # keep going while the motors are on
    drone.recv_match(type="HEARTBEAT", blocking=True)
```

Or loop forever and `break` out when you're done:

```python
while True:
    height = ...
    if height > 9.5:
        break                       # leave the loop
```

Always read a message inside a waiting loop. That's how new data comes in. A loop that only checks
an old value will spin forever.

### `time.sleep`

`time.sleep(5)` pauses the script for 5 seconds. The drone keeps flying while you sleep. Messages
pile up and you read them afterwards.

### `try` / `except`

```python
try:
    while True:
        ...
except KeyboardInterrupt:
    print("Stopped")
```

If an error happens inside `try`, Python jumps to the matching `except` block instead of crashing.
`KeyboardInterrupt` is the "error" you get when you press `Ctrl+C`. Exercise 04 uses this to stop
recording cleanly.

### Lists and dictionaries

```python
corners = [(20, 0), (20, 20), (0, 20), (0, 0)]   # a list of (north, east) pairs
for north, east in corners:
    ...

sample = {"t": 1.5, "up": 9.8}   # a dictionary: names mapped to values
sample["speed"] = 4.2            # add or change one entry
```

### A few more small things

- `pass` does nothing. It fills a spot where Python needs a line, like an empty `elif`. The
  skeletons use it to mark where your code goes.
- `max(a, b)` gives the bigger value, `abs(x)` drops the minus sign, and `math.hypot(x, y)` gives
  √(x² + y²).
- `for i, value in enumerate(items):` loops over a list and gives you the position (0, 1, 2, ...)
  as well as the value.
- `if __name__ == "__main__":` at the bottom of a file means "only run this when the file is run
  directly, not when another file imports it".
- `# noqa: E402` at the end of an import line tells code checkers that the import is late on
  purpose. You can ignore it.

## pymavlink you will see

### Messages

The autopilot sends many kinds of messages, several times a second. Each one has a type name and
some fields. These are the ones the exercises use:

| Message | Useful fields | Units |
| --- | --- | --- |
| `HEARTBEAT` | mode, armed or not (read them with `drone.flightmode` and `drone.motors_armed()`) | |
| `GLOBAL_POSITION_INT` | `lat`, `lon` | degrees × 10<sup>7</sup> |
| | `relative_alt` | millimetres above home |
| | `vx`, `vy`, `vz` | cm/s |
| `LOCAL_POSITION_NED` | `x`, `y`, `z` | metres north, east and **down** from home |
| | `vx`, `vy`, `vz` | m/s |
| `VFR_HUD` | `groundspeed`, `alt` | m/s, m |
| `ATTITUDE` | `roll`, `pitch`, `yaw` | radians |
| `STATUSTEXT` | `text` | messages like `PreArm: ...` |
| `COMMAND_ACK` | `command`, `result` | the reply to a command (`result` 0 means accepted) |

The units matter:

- `lat` and `lon` are whole numbers. `437000000` means 43.7°. Divide by `1e7` (10 million) to get
  degrees. Multiply by `1e7` and turn into an `int` when you send them.
- In `LOCAL_POSITION_NED`, `z` points **down**. A drone 10 m up has `z = -10`.
- Different messages use different units for the same thing. Always check the
  [message list](https://mavlink.io/en/messages/common.html).

To see live messages, type `status GLOBAL_POSITION_INT` in MAVProxy.

### `recv_match`

```python
msg = drone.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)
```

- `type=` is the message type you want. Others are skipped. You can pass a list, like
  `type=["HEARTBEAT", "STATUSTEXT"]`, and check which one you got with `msg.get_type()`.
- `blocking=True` means "wait until one arrives". Without it, you get `None` straight away if
  nothing is waiting.
- `timeout=2` means "but don't wait more than 2 seconds". Leave it out to wait forever.

The result is either a message or `None`. Read fields with a dot: `msg.relative_alt`.

### `set_mode`

```python
drone.set_mode("GUIDED")
```

This asks the autopilot to change mode. It doesn't wait for the change. To be sure, read heartbeats
until `drone.flightmode` equals the mode you asked for.

### Arming

```python
drone.arducopter_arm()
```

This sends the arm command. The autopilot may refuse, for example while it waits for GPS. Check
`drone.motors_armed()` after the next heartbeat, and send it again if needed. Refusals arrive as
`STATUSTEXT` messages that start with `PreArm:`.

### `command_long_send`

Most actions are commands. You send them like this:

```python
drone.mav.command_long_send(
    drone.target_system,                    # which drone
    drone.target_component,                 # which part of it (the autopilot)
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,    # which command
    0,                                      # confirmation: always 0 the first time
    0, 0, 0, 0, 0, 0, 10)                   # param1 to param7
```

Every command has exactly 7 parameters. Each command uses them for different things, and you put 0
in the ones it doesn't use. For `MAV_CMD_NAV_TAKEOFF`, param7 is the height in metres. Look up any
command in the [MAVLink command list](https://mavlink.io/en/messages/common.html#mav_commands) to
see what its 7 parameters mean. ArduPilot's
[Copter commands in GUIDED mode](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html)
page lists the ones Copter supports.

`drone.mav` is the part of the connection that builds and sends messages. Every MAVLink message has
a matching `drone.mav.<name>_send(...)` function, for example `param_set_send` or
`set_position_target_local_ned_send`.

The autopilot answers each command with a `COMMAND_ACK` message.

### Sending a position target

In `GUIDED` mode you can tell the drone where to go with `set_position_target_local_ned_send`. It
takes 16 values. The skeletons that need it give you the full call and tell you which values to
change.

## When your script doesn't work

- **It stops at `Waiting for heartbeat...`.** SITL isn't running, or it's on another port.
- **`NotImplementedError`.** You haven't filled in that function in `mydrone.py` yet.
- **`AttributeError: 'NoneType' object has no attribute ...`.** `recv_match` timed out and returned
  `None`, and you read a field from it. Check for `None` first.
- **The drone ignores a command.** Check the mode (usually needs `GUIDED`) and look for
  `COMMAND_ACK` or `STATUSTEXT` messages in MAVProxy.
- **The drone was fine, now it won't arm.** Restart SITL with `-w`.
