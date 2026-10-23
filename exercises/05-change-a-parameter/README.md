# 05 Change a parameter

**Goal:** change one parameter and measure what it does. The script flies the same 40 m leg twice,
with `WP_SPD` set to 2 m/s and then 8 m/s, and prints the top speed and time for each.

## What you need to know

**Parameters** are the autopilot's settings. ArduPilot has more than a thousand of them: speeds,
tuning gains, safety limits, which sensors are fitted. They are stored on the drone and survive a
restart. (That's why `-w` exists: to wipe them.)

`WP_SPD` is the top horizontal speed, in m/s, when the drone flies to a target in `GUIDED` or `AUTO`.
Look it up in the [Copter parameter list](https://ardupilot.org/copter/docs/parameters.html).

> **Note:** parameter names change between ArduPilot versions. This course uses Copter 4.7, where
> it's `WP_SPD` in m/s. Older guides call it `WPNAV_SPEED`, in cm/s.

You can try it by hand first in MAVProxy:

```
param show WP_SPD
param set WP_SPD 3
```

From Python, you send `PARAM_SET`, and the drone answers with `PARAM_VALUE` to confirm the new value.
As always: send, then wait for the confirmation.

One catch: `GUIDED` reads `WP_SPD` when the mode starts. So after each change, the script switches to
`BRAKE` and back to `GUIDED`. (`AUTO` missions use a new value straight away.)

**Speed from velocity.** `LOCAL_POSITION_NED` has `vx` (north) and `vy` (east) in m/s. The
horizontal speed is `math.hypot(vx, vy)`, which is √(vx² + vy²).

## Steps

1. Try `param set WP_SPD 3` by hand in MAVProxy, then fly somewhere on the map. Does it fly at 3 m/s?
2. Fill in `set_param()` in [mydrone.py](../mydrone.py).
3. In [starter.py](starter.py), fill in the two `TODO`s: keep the highest speed in `fly_leg()`, and
   set the parameter before each leg.
4. Run it with SITL running:
   ```bash
   python3 exercises/05-change-a-parameter/starter.py
   ```

## Hints

- `top_speed = max(top_speed, speed)` keeps the bigger of the two.
- In `set_param()`, the reply's `param_id` is a string, like `"WP_SPD"`. Compare it with `name`.
- If `set_param()` waits forever, print every `PARAM_VALUE` you receive and look at what comes back.

## What you should see

Something like this. Your numbers will be a little different:

```
WP_SPD   top speed   time for 40 m
 2 m/s     2.1 m/s       21.0 s
 8 m/s     8.0 m/s       10.0 s
```

The top speed follows the parameter, and the leg takes about half the time at 8 m/s. In Webots
(stage 2) the numbers come out a little different, because the physics model is different.

## Questions to think about

1. 40 m at 8 m/s is 5 seconds. Why does it take longer than that?
2. What else could limit the top speed if you set `WP_SPD` to 30?
3. Why should a script check the `PARAM_VALUE` reply instead of trusting that the change worked?

## Try next

- Do the same with `WP_ACC` (how hard it speeds up, in m/s²).
- Try `ATC_ANGLE_MAX` (the most it may tilt, in degrees). Does a smaller limit lower the top speed?
- Use exercise 04 to plot a leg at each speed.
