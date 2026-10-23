# Setup guide

This page tells you what to install and which official pages to read. It doesn't do the install
for you. Reading the official docs is part of the course: when something breaks later, you will
know where to look.

Plan for about an hour. Most of that is waiting for downloads and the first build.

When you're done, run `python3 check_setup.py` from this repo. It tells you which steps worked.

## What you are installing

| Piece | What it is | Why you need it |
| --- | --- | --- |
| ArduPilot | the autopilot source code | SITL is built from it |
| SITL | ArduPilot built to run on your computer | this is the "drone" you fly |
| `sim_vehicle.py` | a script in ArduPilot's `Tools/autotest` folder | starts SITL and MAVProxy together with sensible settings |
| MAVProxy | a ground station you use from the terminal | lets you fly by typing commands, and passes messages on to your scripts |
| pymavlink | a Python library for MAVLink | your scripts use it to talk to the drone |
| Webots (stage 2) | a 3D robot simulator | gives the drone a 3D world, physics and sensors |

MAVLink is the message format drones and ground stations use to talk to each other. Everything you
write in this course speaks MAVLink, so it also works with a real flight controller.

## 1. Your system

ArduPilot is built and tested mostly on Ubuntu Linux. Pick your system below.

### Linux

Use Ubuntu 22.04 or 24.04 if you can. Other distributions work, but the ArduPilot install script is
written for Ubuntu. Install git:

```bash
sudo apt-get update
sudo apt-get install git
```

### macOS

Install the Xcode command line tools and [Homebrew](https://brew.sh):

```bash
xcode-select --install
```

Then read [Setting up the Build Environment (MacOSX)](https://ardupilot.org/dev/docs/building-setup-mac.html).
You run its install script in step 2, after you download ArduPilot.

### Windows

On Windows, you run ArduPilot inside WSL2. WSL2 is a real Ubuntu system that runs inside Windows.
Read [Setup the waf Build Environment on Windows 11 using WSL2](https://ardupilot.org/dev/docs/building-setup-windows11.html).

1. Open PowerShell as administrator and run:
   ```powershell
   wsl --install -d Ubuntu-24.04
   ```
2. Restart your computer when it asks. Then open **Ubuntu** from the Start menu and create a
   username and password.
3. From now on, type every command in this course into the Ubuntu terminal, not PowerShell. Follow
   the Linux steps.

> **Note:** keep your files inside Ubuntu (for example `~/ardupilot`), not under `/mnt/c/`.
> Building from a Windows folder is very slow.

Windows 11 shows Linux windows (the MAVProxy map, Webots) on your normal desktop. This is called
WSLg. On Windows 10 you need a recent update for it. Run `wsl --update` in PowerShell if windows
don't appear.

## 2. ArduPilot

Read [Downloading the code / Using Git](https://ardupilot.org/dev/docs/where-to-get-the-code.html)
and [Setting up the Build Environment (Linux/Ubuntu)](https://ardupilot.org/dev/docs/building-setup-linux.html).

Download ArduPilot into your home folder and switch to the stable Copter release this course uses:

```bash
cd ~
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Copter-4.7.2
git submodule update --init --recursive
```

Then run the install script for your system. It installs the compilers and Python tools ArduPilot
needs.

```bash
Tools/environment_install/install-prereqs-ubuntu.sh -y    # Linux and WSL2
Tools/environment_install/install-prereqs-mac.sh          # macOS
```

When it finishes, close the terminal and open a new one (or run `. ~/.profile`). This loads the
new settings, including the folder that holds `sim_vehicle.py`.

> **Tip:** if the course is ever behind ArduPilot, a newer `Copter-4.x` tag should still work. All
> exercises were tested on Copter 4.7.2.

## 3. Python packages

The exercises need pymavlink, MAVProxy, numpy and matplotlib. Read
[Installing MAVProxy](https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html).

On Ubuntu, the ArduPilot install script creates a Python virtual environment called
`~/venv-ardupilot` and turns it on in every new terminal. A virtual environment is a private set of
Python packages, so you don't break the Python your system uses. Install the course packages into
it:

```bash
cd path/to/this/repo
python3 -m pip install -r requirements.txt
```

If your system has no virtual environment turned on (the prompt doesn't start with
`(venv-ardupilot)`), make one first:

```bash
python3 -m venv ~/venv-ardupilot
source ~/venv-ardupilot/bin/activate
```

You need to run the `source` line again in every new terminal, or add it to `~/.bashrc` (Linux) or
`~/.zshrc` (macOS).

## 4. Build SITL

Read [Building the code](https://ardupilot.org/dev/docs/building-the-code.html), and the
[BUILD.md](https://github.com/ArduPilot/ardupilot/blob/master/BUILD.md) file in the ArduPilot repo.
ArduPilot uses a build tool called waf.

```bash
cd ~/ardupilot
./waf configure --board sitl
./waf copter
```

The first build takes 5 to 15 minutes. When it works, the last line says `'copter' finished
successfully`, and the program is at `build/sitl/bin/arducopter`.

## 5. First run

Read [Setting up SITL on Linux](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html) and
[Using SITL for ArduPilot Testing](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html).

```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map -w
```

`-w` wipes saved settings and loads the defaults. You only need it the first time, or when you want
a fresh start.

You should see three things: a terminal with a `STABILIZE>` prompt, a console window with the
drone's status, and a map with a drone icon. After about 30 seconds the console says
`EKF3 IMU0 is using GPS`. Your setup works. Close everything with `Ctrl+C` in the terminal.

> **Note:** if `sim_vehicle.py` is "command not found", open a new terminal so `~/.profile` loads.
> You can also run it by its full path, `~/ardupilot/Tools/autotest/sim_vehicle.py`.

If the map or console doesn't open, MAVProxy may be missing wxPython. Run without `--map --console`
for now. The text prompt is all you need.

Now run the checker:

```bash
python3 check_setup.py
```

It starts its own short copy of SITL and waits for a heartbeat (a hello message the autopilot sends
once a second). If ArduPilot is not in `~/ardupilot`, add `--ardupilot /path/to/ardupilot`.

## 6. Webots (stage 2)

You don't need this until stage 2. Read
[Installing Webots](https://cyberbotics.com/doc/guide/installing-webots) and
[Using SITL with Webots Python](https://ardupilot.org/dev/docs/sitl-with-webots-python.html).

Install Webots R2025a from [cyberbotics.com](https://cyberbotics.com/). The ArduPilot page says
Webots 2023a or newer works.

- **Linux and WSL2:** download the `.deb` file and install it with
  `sudo apt install ./webots_2025a_amd64.deb`.
- **macOS:** open the `.dmg` file and drag Webots to Applications.

On Windows, install Webots inside Ubuntu (WSL2), like on Linux. That way SITL and Webots can find
each other on `127.0.0.1`. The ArduPilot page also describes Webots on Windows with SITL in WSL2.
That works too, but you have to pass IP addresses around, and `check_setup.py` can't see a Webots
installed on the Windows side.

Check it:

```bash
python3 check_setup.py --webots
```

## Reading list

You don't need to read all of this now. Come back when an exercise points you here.

- ArduPilot: [SITL overview](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html),
  [Using SITL](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- MAVProxy: [documentation](https://ardupilot.org/mavproxy/index.html),
  [cheatsheet](https://ardupilot.org/mavproxy/docs/getting_started/cheatsheet.html)
- MAVLink from code: [MAVLink basics](https://ardupilot.org/dev/docs/mavlink-basics.html),
  [Copter commands in GUIDED mode](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html),
  [pymavlink guide](https://mavlink.io/en/mavgen_python/),
  [list of all messages](https://mavlink.io/en/messages/common.html)
- Copter: [flight modes](https://ardupilot.org/copter/docs/flight-modes.html),
  [parameters](https://ardupilot.org/copter/docs/parameters.html)
- Webots: [tutorials](https://cyberbotics.com/doc/guide/tutorials),
  [your first simulation](https://cyberbotics.com/doc/guide/tutorial-1-your-first-simulation-in-webots)
