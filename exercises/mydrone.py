"""Your own helper functions for flying the drone.

You fill these in during the exercises. Each function says which exercise it belongs to.
Delete the `raise NotImplementedError(...)` line and write the function body in its place.

Other scripts use these functions like this:

    import mydrone
    drone = mydrone.connect()
    mydrone.arm(drone)
"""
import time

from pymavlink import mavutil

# These numbers tell set_position_target_local_ned which of its values to use.
# Each bit that is 1 means "ignore this value". You don't need to change them.
USE_POSITION = 0b0000111111111000
USE_VELOCITY = 0b0000111111000111


# ---------------------------------------------------------------- exercise 02

def connect(address="udp:127.0.0.1:14550"):
    """Open a connection, wait for the first heartbeat and return the connection."""
    # TODO: open the connection with mavutil.mavlink_connection(address),
    #       wait for a heartbeat, print which system you connected to, and return it.
    raise NotImplementedError("connect(): exercise 02")


def set_mode(drone, mode):
    """Change flight mode and wait until the drone reports the new mode."""
    # TODO: ask for the mode with drone.set_mode(mode).
    #       Then keep reading HEARTBEAT messages until drone.flightmode == mode.
    raise NotImplementedError("set_mode(): exercise 02")


def arm(drone, timeout=60):
    """Arm the motors. Keep trying until it works or `timeout` seconds pass."""
    # TODO: while the motors are not armed (drone.motors_armed()):
    #         - send the arm command (drone.arducopter_arm())
    #         - read one HEARTBEAT or STATUSTEXT message, with a timeout of about 2 s
    #         - if it is a STATUSTEXT, print msg.text so you can see why arming failed
    #         - if more than `timeout` seconds have passed, raise RuntimeError("...")
    # Hint: work out the deadline before the loop, like listen.py does.
    raise NotImplementedError("arm(): exercise 02")


def altitude(drone):
    """Return the height above home in metres."""
    # TODO: read one GLOBAL_POSITION_INT message and return relative_alt in metres.
    #       relative_alt is in millimetres.
    raise NotImplementedError("altitude(): exercise 02")


def takeoff(drone, target):
    """Climb to `target` metres and return when the drone is nearly there.

    The drone must be in GUIDED mode and armed.
    """
    # TODO: send MAV_CMD_NAV_TAKEOFF with command_long_send. The height goes in param7.
    # TODO: then wait until altitude(drone) is at least 95% of target.
    #       (It may never reach exactly `target`, so don't wait for that.)
    raise NotImplementedError("takeoff(): exercise 02")


def land(drone):
    """Switch to LAND and return once the drone has landed and disarmed itself."""
    # TODO: use your set_mode(), then read heartbeats until the motors are no longer armed.
    raise NotImplementedError("land(): exercise 02")


# ---------------------------------------------------------------- exercise 05

def set_param(drone, name, value):
    """Set a parameter and wait until the drone confirms the new value."""
    # Sends the new value. The name must be bytes, so .encode() turns "WP_SPD" into b"WP_SPD".
    drone.mav.param_set_send(drone.target_system, drone.target_component, name.encode(),
                             value, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    # TODO: the drone replies with a PARAM_VALUE message. Read PARAM_VALUE messages until you get
    #       one where msg.param_id == name and msg.param_value is (almost) equal to value.
    #       Floats are not exact, so compare with abs(a - b) < 0.001.
    # Hint: use a timeout. If nothing comes back in 3 s, send the value again.
    raise NotImplementedError("set_param(): exercise 05")


# ---------------------------------------------------------------- given to you

def position(drone):
    """Return the latest position as (north, east, up) in metres from home."""
    msg = drone.recv_match(type="LOCAL_POSITION_NED", blocking=True)
    return msg.x, msg.y, -msg.z      # z points down, so up = -z


def move_to(drone, north, east, up):
    """Ask the drone to fly to a point (metres from home). Returns straight away.

    Only works in GUIDED mode.
    """
    drone.mav.set_position_target_local_ned_send(
        0,                                   # time: 0 is fine
        drone.target_system, drone.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # positions are measured from home
        USE_POSITION,                        # use x, y, z and ignore the rest
        north, east, -up,                    # x, y, z (z points down)
        0, 0, 0,                             # vx, vy, vz (ignored)
        0, 0, 0,                             # ax, ay, az (ignored)
        0, 0)                                # yaw, yaw rate (ignored)


def move_forward(drone, speed):
    """Fly forward, the way the drone faces, at `speed` m/s.

    Copter stops if it gets no new velocity for a few seconds, so call this
    at least once a second.
    """
    drone.mav.set_position_target_local_ned_send(
        0, drone.target_system, drone.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # directions relative to the drone's nose
        USE_VELOCITY,                               # use vx, vy, vz and ignore the rest
        0, 0, 0,
        speed, 0, 0,                                # vx is forward
        0, 0, 0,
        0, 0)


def wait(seconds):
    """Pause the script. The drone keeps doing what it was doing."""
    time.sleep(seconds)
