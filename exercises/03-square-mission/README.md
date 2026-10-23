# 03 Fly a square mission

**Goal:** upload a list of waypoints, then let the autopilot fly them on its own in `AUTO` mode. The
drone takes off to 10 m, flies a 20 m square, comes home and lands.

![Square mission in Webots](../../docs/images/square-mission.gif)

*This is the same exercise running in Webots, which you'll get to in stage 2. In stage 1 you watch
it on the SITL map.*

## What you need to know

**A mission** is a numbered list of items stored on the drone. Each item is a command with a
position. The ones you need:

| Command | What it does |
| --- | --- |
| `MAV_CMD_NAV_TAKEOFF` | climb to a height |
| `MAV_CMD_NAV_WAYPOINT` | fly to a latitude, longitude and height |
| `MAV_CMD_NAV_RETURN_TO_LAUNCH` | fly home and land |

Item 0 is always home. ArduPilot replaces it with the real home position, so you can send anything
there.

**Uploading** is a short back-and-forth. Your script says how many items there are. Then the drone
asks for each one by number, and your script sends it. At the end the drone says it got them all:

```
script -> MISSION_COUNT (7 items)
drone  -> MISSION_REQUEST 0     script -> MISSION_ITEM_INT 0
drone  -> MISSION_REQUEST 1     script -> MISSION_ITEM_INT 1
...
drone  -> MISSION_ACK
```

The `upload()` function in the skeleton already does this. Read it and make sure you follow it.

**Latitude and longitude.** Mission positions are in degrees, not metres. Near the ground:

- 1 degree of latitude (north-south) is about 111,320 m everywhere.
- 1 degree of longitude (east-west) is 111,320 m × cos(latitude). It gets shorter as you go
  towards the poles.

`MISSION_ITEM_INT` sends degrees × 10<sup>7</sup> as whole numbers, like `GLOBAL_POSITION_INT`.

**`MISSION_ITEM_REACHED`** is a message the drone sends each time it finishes an item. Its `seq`
field is the item number.

Read [Copter mission commands](https://ardupilot.org/copter/docs/mission-command-list.html) and the
[mission protocol](https://mavlink.io/en/services/mission.html) (just the "Upload a Mission" part).

## Steps

1. Fill in `square()`. It returns the four corners as `(north, east)` pairs in metres, ending back at
   `(0, 0)`.
2. Fill in `offset()`. It turns "this many metres north and east of a point" into a new latitude and
   longitude. Use the two facts above. `math.cos` needs radians, so use
   `math.cos(math.radians(lat))`.
3. Test both functions before you fly. Type `python3` to open a Python shell, paste in
   `import math`, `METRES_PER_DEGREE = 111_320` and your two functions, then try
   `offset(43.0, -79.0, 20, 0)`. 20 m north should add about 0.00018 to the latitude.
4. Fill in the last `TODO`: after switching to `AUTO`, print each `MISSION_ITEM_REACHED` until the
   drone disarms.
5. Run it with SITL running:
   ```bash
   python3 exercises/03-square-mission/starter.py
   ```

## Hints

- Draw the square on paper first. Which corner comes first doesn't matter, as long as you go round
  in order.
- If the drone flies off in a strange direction, check `offset()`. Did you mix up latitude and
  longitude, or forget the `cos`?
- If the upload says "No reply from the drone", is SITL running and is nothing else using port
  14550?
- Copter only starts a mission in `AUTO` if it's already flying or the first item is a takeoff. The
  script takes off in `GUIDED` first, so either works.

## What you should see

```
Connected to system 1
Uploaded 7 mission items
Reached item 1
Reached item 2
Reached item 3
Reached item 4
Reached item 5
Reached item 6
Landed and disarmed
```

On the map, the mission shows up as a square of numbered points, and the drone's trail follows it.
Type `wp list` in MAVProxy to see the mission stored on the drone.

## Questions to think about

1. Why does the mission need a separate item for takeoff when the script already took off?
2. Why do you need `cos(latitude)` for east, but not for north?
3. What would go wrong if you sent `lat` in degrees without multiplying by 10<sup>7</sup>?

## Try next

- Make it a triangle, or a different height at each corner.
- Add a `MAV_CMD_NAV_LOITER_TIME` item to wait 5 seconds at one corner. Look up which of its 7
  parameters is the time.
- Plan the same mission in [QGroundControl](https://qgroundcontrol.com/) or Mission Planner instead.
  Connect it over UDP 14550 (stop your script first).
