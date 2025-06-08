# Mouse Spam Recorder

A tool to record and replay mouse movements and clicks automatically.

<img src="https://i.imgur.com/7e5DCqF.jpeg"/>

## Features
- Record mouse cursor positions using `MouseInfo`
- Save and load custom movement sequences
- Automate repeated mouse clicks with customizable delay
- Cancel playback at any time

---

## 📖 How to Use
### 1. Record Mouse Movements
- Open the app and click **"Record Movements"**.
- This launches the `MouseInfo` utility (used to log mouse coordinates).
- In `MouseInfo`:
  - **Uncheck** the `3 Sec. Button Delay` checkbox.
  - Move your mouse to the desired spot and press **"Log XY (F6)"**.
  - Repeat to log multiple positions.
- Click **"Save Log"** to export your coordinates and close `MouseInfo`.

### 2. Load Coordinates
- Click **"Load Coordinates"** in the main program.
- A window appears with your logged positions.
- Here, you can:
  - Add right clicks
  - Edit or remove coordinates
- Click **"Save and Close"** when done.

### 3. Set Replay Settings
- In the main window:
  - Set the **delay** (in seconds) between each click.
  - Set the **number of repetitions** for the sequence.

### 4. Start Automation
- Click **"Start Replay"** to begin.
- To cancel:
  - Click **"Cancel Replay"**, or
  - Press the **`ESC` key** on your keyboard.

---

## 🚀 Installation

### Option 1: Download Release
Grab the latest build: [Download v1.0](https://github.com/Gnomee1337/mouse-spam-recorder/releases/tag/v1.0)

### Option 2: Run from Source
```bash
$ pip install -r requirements.txt
$ python spam_v2.py
```

# Build executable:
```
$ pyinstaller --onefile --windowed --hidden-import=mouseinfo .\spam_v2.py
```
