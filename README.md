# Claude Vision Robot Control

This project demonstrates autonomous robot navigation controlled entirely through natural language, where a LEGO robot receives goals in plain English and navigates using an AI vision loop. Behavior emerges entirely from prompt engineering and strategic instructions determine task completion time without changing any code. This shows how LLMs can translate abstract goals into physical actions, making robotics accessible to anyone who can articulate objectives rather than write algorithms.

## How It Works: The AI Vision Loop

![flow chart](diagram.png "AI-Vision-Loop")

### Step by step

1. **Capture** — OpenCV grabs a JPEG frame from the MacBook webcam (which is actually the iPhone via Camo)
2. **Send to Claude** — The frame + the mission goal are sent to Claude as a vision prompt
3. **Reason** — Claude describes what it sees in one sentence, checks its recent move history to avoid repetition, then calls `drive_robot(direction, angle)`
4. **Publish** — `drive.py` pushes a `robot_command` JSON payload to a PyScript WebSocket channel
5. **Bridge** — `bridge.py` is subscribed to the same channel; it receives the command and writes it to the SPIKE over BLE
6. **Execute** — The SPIKE first turns to the specified angle, then drives for 1 second in the specified direction
7. **Loop** — Control returns to step 1; this repeats until Claude calls `direction="x"` to signal the task is complete

---

## Dashboard

[![Dashboard Demo](https://img.youtube.com/vi/1IiqRllre2M/maxresdefault.jpg)](https://www.youtube.com/watch?v=1IiqRllre2M)

A live web interface displays the robot's decision making in real time. The camera view shows what the robot sees, while the activity log reveals Claude's observations and reasoning for each movement command. Users enter a goal in plain English. This dashboard lets users see exactly how the LLM translates visual input into physical actions. Notice how no custom machine learning or training is required. Each decision comes from sending an image from a phone camera to Claude’s API alongside the message history. 

---

## Experiment

The robot was tasked with finding a water bottle using five prompts of increasing detail.

![results](results.png "AI-Vision-Loop")

**5 token prompt:** “Find the water bottle.”  - **201s.**

**100 token prompt:** “Locate the greenish-teal water bottle behind you, between some boxes and the TV stand. Start by turning around with a stationary 180° turn, then survey the area. Once you see boxes, do a 45° turn, the water bottle is to the right of the boxes. Once you spot the bottle, switch to forward movement with fine 15° adjustments to center on it. Avoid oscillating. Stop when the bottle is centered and close.” – **20s**

### Outcome

Detailed instructions reduced task completion time from 201 seconds to 20 seconds without any code changes, meaning that prompt complexity directly impacts performance. This enables a new kind of robotics competition, where participants compete through prompt engineering rather than programming, making robotics accessible to anyone who can articulate a strategy in plain English.

## Camera Setup: Camo App

The iPhone is used because it provides a much better image than a MacBook webcam and can be freely positioned — overhead on a stand, angled from the side, etc.

**[Camo](https://reincubate.com/camo/)** makes the iPhone appear as a standard webcam on macOS over USB or WiFi.

**Setup:**
1. Install **Camo** on your iPhone (App Store)
2. Install the **Camo companion app** on your MacBook
3. Connect the phone to the MacBook via USB (lowest latency) or enable WiFi mode
4. The iPhone will now appear as a webcam named `Camo` — `camera.py` picks it up via OpenCV as the default capture device (`index 0`)
5. Mount the phone with a clear view of the robot's workspace

---

## Project Structure

```
RobotControl/
├── server/
│   ├── main.py              # Orchestrator: starts dashboard, handles BLE, runs missions
│   ├── agent.py             # Claude vision loop — captures photo, calls Claude API, executes tool
│   ├── camera.py            # OpenCV camera capture → base64 JPEG
│   ├── drive.py             # Publishes motor commands to PyScript WebSocket channel
│   ├── bridge.py            # Subscribes to PyScript channel, forwards commands via BLE to SPIKE
│   ├── tools.py             # Claude tool definition for drive_robot (direction + angle schema)
│   ├── dashboard_server.py  # Local WebSocket server (ws://localhost:8765) for the dashboard
│   └── dashboard.html       # Browser dashboard UI
└── spike/
    └── spike.py             # MicroPython code running on the SPIKE hub
```

---

## Setup

### Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set
- A [PyScript Apps](https://pyscriptapps.com/) channel (used as the WebSocket message broker)
- Camo app on iPhone + MacBook
- LEGO SPIKE Prime or Essential with `BLE_CEEO` library installed

### Install dependencies

```bash
pip install anthropic bleak websockets websocket-client opencv-python
```

### Configure the PyScript channel

In both `server/bridge.py` and `server/drive.py`, update the channel settings:

```python
USER    = "your-pyscript-username"
PROJECT = "your-project-name"
CHANNEL = "your-channel-name"
```

### Load code onto the SPIKE

Copy `spike/spike.py` onto the SPIKE hub using the SPIKE app or a MicroPython-compatible tool. The robot will advertise as BLE peripheral `"jj"` and wait for connections.

> To use a different BLE device name, change `"jj"` in `bridge.py` (`find_ble_device`) and `"Spike"` in `spike.py` (`Yell("Spike", ...)`) accordingly.

### Run

```bash
cd server
python main.py
```

Open `server/dashboard.html` in your browser, then:
1. Click **Connect** to scan for and connect to the SPIKE over BLE
2. Type a mission goal (e.g. `"Navigate to the red ball"`)
3. Click **Start Mission** — the vision loop begins

---

## Robot Commands

Claude controls the robot using a single tool:

### `drive_robot(direction, angle)`

The robot **turns first**, then **drives for 1 second**.

| Parameter | Options | Description |
|---|---|---|
| `direction` | `f`, `b`, `s`, `x` | Forward, Backward, Stationary (turn in place), Complete |
| `angle` | `0, ±15, ±45, ±90, ±135, 180` | Clockwise (positive) or counter-clockwise (negative) turn in degrees |

Claude's built-in strategy (from `tools.py`):
- Survey first with stationary turns before approaching
- Use coarse scans (45–90°) to find the target, fine adjustments (15°) to approach
- Detect and break out of oscillation patterns (e.g. alternating ±45°)
- Call `direction="x"` only when the task is definitively complete

---

## Credits

- [Anthropic Claude](https://anthropic.com/) — vision + reasoning
- [PyScript](https://pyscript.net/) — WebSocket channel broker
- [Bleak](https://github.com/hbldh/bleak) — BLE communication
- [Camo by Reincubate](https://reincubate.com/camo/) — iPhone as MacBook webcam
- [Tufts CEEO](https://ceeo.tufts.edu/) — Center for Engineering Education and Outreach

---

## License

MIT
