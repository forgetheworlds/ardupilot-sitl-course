#!/usr/bin/env python3
"""Check that everything the course needs is installed and working.

This script only looks. It never installs or changes anything.

    python3 check_setup.py            stage 1: Python, MAVProxy, ArduPilot SITL
    python3 check_setup.py --webots   stage 1 plus stage 2: Webots

If ArduPilot isn't in ~/ardupilot, point to it with --ardupilot PATH or the
ARDUPILOT_DIR environment variable.
"""
import argparse
import contextlib
import importlib
import io
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SETUP = "docs/setup.md"
RESULTS = []


def report(status, name, detail="", fix=""):
    RESULTS.append(status)
    print(f"[{status}] {name}" + (f": {detail}" if detail else ""))
    if fix and status == "FAIL":
        print(f"       fix: {fix}")


def check_python():
    version = sys.version_info
    text = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 10):
        report("PASS", "Python", text)
        return True
    report("FAIL", "Python", f"{text} is too old, the course needs 3.10 or newer",
           f"{SETUP}#3-python-packages")
    return False


def check_module(module, label):
    try:
        mod = importlib.import_module(module)
    except ImportError as error:
        report("FAIL", label, f"can't import {module} ({error})",
               f"{SETUP}#3-python-packages (did you activate your virtual environment?)")
        return False
    version = getattr(mod, "__version__", "")
    report("PASS", label, f"imported from {Path(mod.__file__).parent}" + (f", {version}" if version else ""))
    return True


def check_mavproxy_command():
    path = shutil.which("mavproxy.py") or shutil.which("mavproxy")
    if path:
        report("PASS", "mavproxy.py command", path)
        return True
    report("FAIL", "mavproxy.py command", "not on your PATH",
           f"{SETUP}#3-python-packages (sim_vehicle.py starts MAVProxy with this command)")
    return False


def find_ardupilot(given):
    candidates = [given] if given else [os.environ.get("ARDUPILOT_DIR"), Path.home() / "ardupilot"]
    for candidate in candidates:
        if candidate and (Path(candidate) / "Tools/autotest/sim_vehicle.py").is_file():
            return Path(candidate).expanduser().resolve()
    return None


def check_ardupilot(given):
    ardupilot = find_ardupilot(given)
    if ardupilot is None:
        where = given or os.environ.get("ARDUPILOT_DIR") or "~/ardupilot"
        report("FAIL", "ArduPilot source", f"no Tools/autotest/sim_vehicle.py in {where}",
               f"{SETUP}#2-ardupilot (or pass --ardupilot PATH)")
        return None
    version = "unknown version"
    header = ardupilot / "ArduCopter/version.h"
    if header.is_file():
        for line in header.read_text(errors="ignore").splitlines():
            if "THISFIRMWARE" in line and '"' in line:
                version = line.split('"')[1]
                break
    report("PASS", "ArduPilot source", f"{ardupilot} ({version})")
    return ardupilot


def check_binary(ardupilot):
    binary = ardupilot / "build/sitl/bin/arducopter"
    if binary.is_file() and os.access(binary, os.X_OK):
        age = (time.time() - binary.stat().st_mtime) / 86400
        report("PASS", "ArduCopter SITL build", f"{binary} (built {age:.0f} days ago)")
        return binary
    report("FAIL", "ArduCopter SITL build", f"{binary} not found",
           f"{SETUP}#4-build-sitl (run ./waf configure --board sitl && ./waf copter)")
    return None


def free_port_block(base=5760):
    """SITL listens on TCP 5760 + 10 * instance. Pick an instance whose port is free."""
    for instance in range(5, 40):
        port = base + 10 * instance
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return instance, port
    return None, None


def check_sitl_boot(ardupilot, binary, timeout):
    from pymavlink import mavutil

    instance, port = free_port_block()
    if instance is None:
        report("FAIL", "SITL boot", "no free TCP port to start a test copy of SITL",
               "close other copies of SITL and try again")
        return False
    defaults = ardupilot / "Tools/autotest/default_params/copter.parm"
    workdir = tempfile.mkdtemp(prefix="sitl-check-")
    command = [str(binary), "--model", "+", "--speedup", "1", "-I", str(instance), "-w",
               "--defaults", str(defaults)]
    sitl = subprocess.Popen(command, cwd=workdir, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    started = time.time()
    try:
        link = None
        while time.time() - started < timeout and link is None:
            if sitl.poll() is not None:
                break
            try:
                with contextlib.redirect_stdout(io.StringIO()):  # hide pymavlink's retry messages
                    link = mavutil.mavlink_connection(f"tcp:127.0.0.1:{port}", autoreconnect=False,
                                                      retries=0)
            except OSError:
                time.sleep(0.5)
        if link is None:
            code = sitl.poll()
            detail = f"SITL exited with code {code}" if code is not None else "never opened its port"
            report("FAIL", "SITL boot", detail, f"{SETUP}#4-build-sitl (try rebuilding with ./waf copter)")
            return False
        heartbeat = link.wait_heartbeat(timeout=max(1, timeout - (time.time() - started)))
        if heartbeat is None:
            report("FAIL", "SITL boot", f"started, but no heartbeat within {timeout} s",
                   f"{SETUP}#5-first-run (a slow or busy computer can cause this; close other programs)")
            return False
        kind = mavutil.mavlink.enums["MAV_TYPE"][heartbeat.type].name
        report("PASS", "SITL boot", f"heartbeat from system {link.target_system} ({kind}) "
               f"after {time.time() - started:.1f} s")
        link.close()
        return True
    finally:
        sitl.terminate()
        try:
            sitl.wait(5)
        except subprocess.TimeoutExpired:
            sitl.kill()
        shutil.rmtree(workdir, ignore_errors=True)


def find_webots():
    home = os.environ.get("WEBOTS_HOME")
    candidates = [shutil.which("webots"),
                  home and str(Path(home) / "webots"),
                  home and str(Path(home) / "Contents/MacOS/webots"),
                  "/Applications/Webots.app/Contents/MacOS/webots",
                  "/usr/local/webots/webots",
                  "/snap/bin/webots"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def check_webots(ardupilot):
    webots = find_webots()
    if webots is None:
        report("FAIL", "Webots", "not found on PATH or in the usual install folders",
               "docs/setup.md#6-webots-stage-2 (or set WEBOTS_HOME)")
        return False
    try:
        out = subprocess.run([webots, "--version"], capture_output=True, text=True, timeout=30)
        version = (out.stdout + out.stderr).strip().splitlines()[-1]
    except (subprocess.SubprocessError, IndexError, OSError):
        version = "version unknown"
    report("PASS", "Webots", f"{webots} ({version})")
    if ardupilot is not None:
        example = ardupilot / "libraries/SITL/examples/Webots_Python/worlds/iris.wbt"
        if example.is_file():
            report("PASS", "ArduPilot Webots example", str(example.parent.parent))
        else:
            report("FAIL", "ArduPilot Webots example", f"{example} missing",
                   "your ArduPilot copy is too old; check out Copter-4.7 or newer")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--webots", action="store_true", help="also check stage 2 (Webots)")
    parser.add_argument("--ardupilot", help="path to your ArduPilot folder (default: ~/ardupilot)")
    parser.add_argument("--timeout", type=float, default=60, help="seconds to wait for SITL (default 60)")
    args = parser.parse_args()

    print(f"Checking your setup on {platform.system()} {platform.release()}\n")
    if os.name == "nt":
        print("You're running this in Windows itself. ArduPilot SITL runs inside WSL2 (Ubuntu),")
        print(f"so open your Ubuntu terminal and run it there instead. See {SETUP}#windows.\n")

    if not check_python():
        print("\nFix Python first, then run this again.")
        return 1
    have_pymavlink = check_module("pymavlink", "pymavlink")
    check_module("MAVProxy", "MAVProxy")
    check_mavproxy_command()

    ardupilot = check_ardupilot(args.ardupilot)
    binary = check_binary(ardupilot) if ardupilot else None
    if ardupilot is None:
        report("SKIP", "ArduCopter SITL build", "needs the ArduPilot source first")
    if binary and have_pymavlink:
        check_sitl_boot(ardupilot, binary, args.timeout)
    else:
        report("SKIP", "SITL boot", "needs pymavlink and a SITL build first")

    if args.webots:
        check_webots(ardupilot)
    else:
        print("[----] Webots: not checked (add --webots when you get to stage 2)")

    failed = RESULTS.count("FAIL")
    print()
    if failed:
        print(f"{failed} check(s) failed. Fix the first FAIL above, then run this again;")
        print("later checks often fail only because an earlier one did.")
        return 1
    stage = "stages 1 and 2" if args.webots else "stage 1"
    print(f"All good. You're ready for {stage}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
