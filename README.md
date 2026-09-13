# DualPointer

<p align="center">
  <b>Multi-Monitor Dual Cursor Switcher & YouTube Hover Lock for Windows</b><br>
  Control two independent mouse pointers with a single physical mouse and keep YouTube thumbnail video previews playing across monitors and applications.
</p>

---

## 🎯 The Problems Solved

1. **Multi-Monitor Cursor Travel**: Moving your mouse continuously back and forth across large 4K or ultra-wide multi-monitor setups causes fatigue and wasted time.
2. **YouTube Hover Previews Stopping**: When hovering over a video card on YouTube, an inline preview starts playing. However, as soon as you move your mouse to another screen, switch windows, or click on another app, Windows fires `mouseleave` and `window.blur` events that immediately pause or dismiss the video.

**DualPointer** solves both seamlessly:
- **Dual Cursor Switcher**: Instantly toggles your physical mouse between two saved positions across any monitor with a single keystroke (**`Alt + \`**), leaving a visible, click-through **Ghost Pointer** indicator at the parked location.
- **YouTube Hover Lock (v1.2)**: Runs directly in the browser's main world execution context to intercept `HTMLMediaElement.prototype.pause`, window `blur`, and leave events. When you hover over any video thumbnail, it **automatically locks** after 700ms, keeping the preview playing continuously while you work, type, or click on another screen!

---

## 🚀 Quick Start

### 1. YouTube Hover Lock Browser Extension

#### Installation (Chrome, Edge, Brave)
1. Open your browser and navigate to `chrome://extensions` or `edge://extensions`.
2. Turn ON the **Developer mode** toggle in the top-right corner.
3. Click **Load unpacked** (top-left).
4. Select the `browser-extension` folder in this repository:
   ```text
   ...\dual-pointer\browser-extension
   ```
5. *(Optional)* If you prefer Tampermonkey or Violentmonkey, install [`userscript/youtube-preview-lock.user.js`](userscript/youtube-preview-lock.user.js).

#### How it Works on YouTube
- **Automatic Lock**: Simply hover over any video thumbnail on YouTube for ~0.7 seconds until the preview starts. A blue **`[🔒 Locked]`** badge appears automatically.
- **Continuous Playback**: Move your mouse away, switch monitors, click into other apps, or type—the video preview continues playing uninterrupted!
- **Unlocking**: Hover over another video to transfer the lock, press **`Alt + P`**, press **`Escape`**, or click the blue lock badge to release it.

---

### 2. Dual-Cursor Desktop Utility (`dual_pointer.py`)

#### Requirements
- Windows 10 or 11 (64-bit)
- Python 3.10+
- Dependencies: `pip install -r desktop/requirements.txt`

#### Running
```powershell
python desktop/dual_pointer.py
```
> **Tip:** You can run `pythonw desktop/dual_pointer.py` to run silently in your system notification tray without keeping a terminal window open.

#### Controls
- **`Alt + \`** (Backslash): Toggle physical mouse control between Cursor 1 and Cursor 2.
- **System Tray Icon**: Right-click the DualPointer icon near your Windows clock to:
  - Toggle the click-through Ghost Pointer overlay on/off
  - Toggle audio click confirmation sound
  - Reset saved positions to screen centers
  - Exit

---

## 🎮 The Combined Multi-Screen Workflow

1. Hover over a video thumbnail on YouTube (Monitor 1). The video preview starts, and the blue **`Locked`** badge appears automatically.
2. Press **`Alt + \`**: Your mouse instantly snaps to Monitor 2. A distinct ghost cursor remains parked over the YouTube video on Monitor 1.
3. Work, click, scroll, and type on Monitor 2—the YouTube video on Monitor 1 **keeps playing smoothly without stopping**.
4. Press **`Alt + \`** anytime to instantly return to your exact spot on Monitor 1!

---

## ⚙️ Configuration

Settings are saved automatically in `~/.dualpointer_config.json`:

```json
{
  "hotkey_modifier": "alt",
  "hotkey_key": "\\",
  "ghost_cursor_enabled": true,
  "overlay_size": 44,
  "sound_cues": false
}
```

- **`hotkey_modifier`**: `"alt"`, `"ctrl"`, `"ctrl+alt"`, or `"none"`
- **`hotkey_key`**: `"\\"`, `"c"`, `"f8"`, `"space"`, etc.
- **`ghost_cursor_enabled`**: `true` / `false` (display visual parked indicator)
- **`sound_cues`**: `true` / `false` (subtle audio beep on switch)

---

## 🔬 How the YouTube Hover Lock Works Internally

1. **`world: "MAIN"` Execution**: Runs in the page's main JavaScript context rather than an isolated extension sandbox, giving direct access to DOM prototypes and Custom Elements.
2. **`HTMLMediaElement.prototype.pause` Interception**: Blocks internal calls to `.pause()` on active preview containers while in locked state.
3. **`blur` & `visibilitychange` Suppression**: Suppresses window blur events during the capture phase so YouTube never detects that you moved to another monitor or application.
4. **`MutationObserver` Guard**: Automatically strips `hidden` attributes or `display: none` styles if YouTube attempts to hide the preview player.
5. **250ms Heartbeat**: Resumes video playback if any internal asynchronous timer attempts to suspend playback.

---

## 🧪 Testing

Run the automated test suite:
```powershell
python -m pytest tests/ -v
```

---

## 📂 Repository Structure

```
dual-pointer/
├── desktop/
│   ├── dual_pointer.py          # Main system tray app & hotkey coordinator
│   ├── cursor_manager.py        # Dual-slot coordinate engine & Win32 API
│   ├── ghost_overlay.py         # Transparent click-through overlay window
│   ├── hotkey_manager.py        # Windows RegisterHotKey engine
│   ├── config.py                # Config management
│   └── requirements.txt         # Desktop dependencies
├── browser-extension/
│   ├── manifest.json            # Manifest V3 extension definition
│   ├── content.js               # Main-world event & prototype protection
│   ├── styles.css               # Lock badge styling
│   └── icons/                   # Extension icons
├── userscript/
│   └── youtube-preview-lock.user.js  # Standalone Tampermonkey script
├── tests/
│   ├── test_cursor_manager.py   # Coordinate & bounds tests
│   ├── test_ghost_overlay.py    # Overlay state tests
│   ├── test_hotkey_manager.py   # Key parsing tests
│   └── test_config.py           # Configuration tests
├── docs/
│   ├── USAGE.md                 # Detailed user guide
│   └── plans/                   # Architecture & design specs
└── README.md
```

## 📄 License
MIT
