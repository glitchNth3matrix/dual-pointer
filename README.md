# DualPointer

<p align="center">
  <b>Multi-Monitor Dual Cursor Switcher & YouTube Hover Lock for Windows</b><br>
  Control two independent mouse pointers with a single physical mouse and keep YouTube thumbnail previews playing across screens.
</p>

---

## 🎯 The Problem Solved

1. **Multi-Monitor Mouse Travel**: Moving your mouse continuously back and forth across multiple 4K / wide displays is slow and causes wrist fatigue.
2. **YouTube Hover Previews Pausing**: On YouTube, hovering over a video thumbnail plays an inline preview, but as soon as you move your mouse to another monitor to work, Windows fires a `mouseleave` event and YouTube immediately stops the video.

**DualPointer** solves both:
- **Dual Cursor Switcher**: Instantly toggles your physical mouse control between two saved positions across any monitor with a keystroke (`Alt + \`).
- **Ghost Pointer Overlay**: Shows a sleek, click-through marker where your other pointer is parked.
- **YouTube Hover Lock**: Intercepts leave events so video previews keep playing continuously while you work on your second screen.

---

## 🚀 Quick Start

### 1. Windows Desktop App (`DualPointer`)

#### Requirements
- Windows 10 or 11
- Python 3.10+ (standard packages; uses native Windows User32 APIs for 0% idle CPU)
- Dependencies: `pip install -r desktop/requirements.txt`

#### Running
```bash
# Run in background with system tray icon:
python desktop/dual_pointer.py
```
> **Tip:** You can run `pythonw desktop/dual_pointer.py` to start it silently without a command prompt window, or place a shortcut in your Windows Startup folder (`shell:startup`).

#### Controls
- **Toggle Active Cursor**: Press `Alt + \` (Backslash) to switch between Cursor 1 and Cursor 2.
- **Tray Menu**: Right-click the DualPointer icon in your Windows notification tray to:
  - Toggle Ghost Pointer overlay
  - Toggle audio click confirmation sound
  - Reset saved positions to screen centers
  - Exit

---

### 2. YouTube Hover Lock (Keep Previews Playing)

Choose either the **Browser Extension** (recommended) or the **Userscript**:

#### Option A: Chrome / Edge / Brave Extension
1. Open your browser and navigate to `chrome://extensions` (or `edge://extensions`).
2. Enable **Developer mode** (toggle in top-right or left sidebar).
3. Click **Load unpacked**.
4. Select the `browser-extension` folder from this repository.
5. Visit [youtube.com](https://www.youtube.com). Hover over any video thumbnail and press `Alt + P` to lock the preview!

#### Option B: Tampermonkey / Violentmonkey Userscript
1. Open Tampermonkey or Violentmonkey in your browser.
2. Create a new script and paste the contents of [`userscript/youtube-preview-lock.user.js`](userscript/youtube-preview-lock.user.js).
3. Save. Previews now lock with `Alt + P` or clicking the lock indicator.

---

## 🎮 How to Use Both Together

1. Hover over a video thumbnail on YouTube (Monitor 1) until the preview starts playing.
2. Press `Alt + P` to lock the preview. A small `[🔒 Locked]` badge will appear in the top-right corner of the video.
3. Press `Alt + \` to switch to Cursor 2 on Monitor 2.
4. Your physical mouse is now on Monitor 2 doing your normal work. Cursor 1 stays parked with a ghost pointer on YouTube, and the video preview continues playing smoothly without stopping!
5. When you want to return to YouTube, hit `Alt + \` again to snap back.

---

## ⚙️ Configuration

Settings are saved in `~/.dualpointer_config.json`:

```json
{
  "hotkey_modifier": "alt",
  "hotkey_key": "\\",
  "ghost_cursor_enabled": true,
  "overlay_size": 40,
  "sound_cues": false
}
```

- **`hotkey_modifier`**: `"alt"`, `"ctrl"`, `"ctrl+alt"`, or `"none"`
- **`hotkey_key`**: `"\\"`, `"c"`, `"f8"`, `"space"`, etc.
- **`ghost_cursor_enabled`**: `true` / `false` (display visual parked indicator)
- **`sound_cues`**: `true` / `false` (subtle audio beep on switch)

---

## 🧪 Running Tests

To run the automated unit tests:

```bash
pytest tests/ -v
```

---

## 📂 Project Structure

```
beautiful-hawking/
├── desktop/
│   ├── dual_pointer.py          # Main system tray app & hotkey coordinator
│   ├── cursor_manager.py        # Dual-slot coordinate engine & Win32 API
│   ├── ghost_overlay.py         # Transparent click-through overlay window
│   ├── hotkey_manager.py        # Windows RegisterHotKey engine
│   ├── config.py                # Config management
│   └── requirements.txt         # Desktop dependencies
├── browser-extension/
│   ├── manifest.json            # Manifest V3 extension
│   ├── content.js               # Event capture & hover lock logic
│   ├── styles.css               # Lock badge styling
│   └── icons/                   # Extension icons
├── userscript/
│   └── youtube-preview-lock.user.js  # Tampermonkey userscript
├── tests/
│   ├── test_cursor_manager.py   # Coordinate & bounds tests
│   ├── test_ghost_overlay.py    # Overlay state tests
│   ├── test_hotkey_manager.py   # Key parsing tests
│   └── test_config.py           # Configuration tests
└── README.md
```

## 📄 License
MIT
