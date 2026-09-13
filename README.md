# DualPointer

<p align="center">
  <b>Multi-Monitor Dual Cursor Switcher & YouTube Hover Lock for Windows</b><br>
  Control two independent mouse pointers with a single physical mouse and keep YouTube thumbnail video previews playing across monitors and applications.
</p>

---

## 🎯 The Problems Solved

1. **Multi-Monitor Cursor Travel**: Moving your mouse continuously back and forth across large 4K or ultra-wide multi-monitor setups causes wrist fatigue and wasted motion.
2. **YouTube Hover Previews Stopping**: When hovering over a video card on YouTube, an inline preview starts playing. However, as soon as you move your mouse to another screen, switch windows, or click on another app, Windows fires `mouseleave` and `window.blur` events that immediately pause or dismiss the video.

**DualPointer** solves both seamlessly:
- **Dual Cursor Switcher**: Instantly toggles your physical mouse between two saved positions across any monitor with a single keystroke (**`Alt + \`**) or **Mouse Thumb / Side Button**, leaving a visible, click-through **Ghost Pointer** indicator at the parked location.
- **Landing Ripple Sonar**: Highlights your newly active cursor with an animated sonar ripple pulse so you never lose track of your pointer across multiple high-res displays.
- **YouTube Hover Lock (v1.3)**: Runs directly in the browser's main world execution context to intercept `HTMLMediaElement.prototype.pause`, window `blur`, and leave events. When you hover over any video thumbnail, it **automatically locks**, keeping the preview playing continuously while you work, type, or click on another screen!
- **Interactive Extension Popup UI**: Clean dark-mode popup menu with customization toggles, hover delay slider (200ms–2000ms), auto-unmute, and auto-looping controls.

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

#### Extension Popup & Controls
Click the **YouTube Hover Lock** icon in your browser toolbar to open the settings popup:
- **Status Indicator**: Displays real-time status (`Active on YouTube` or `Standby`).
- **Master Protection Toggle**: Instant enable/disable switch.
- **Auto-Lock on Hover**: Toggle automatic locking with a live **Hover Delay Slider** (200ms to 2000ms).
- **Auto-Loop Video**: Keeps preview videos looping seamlessly when they finish.
- **Auto-Unmute Audio**: Plays audio immediately when a preview locks.
- **On-Screen Badge Toggle**: Shows/hides the floating `[Locked]` badge with 1-click `[🔇/🔊]` sound toggle.

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
- **`Alt + \`** (Backslash) or **Mouse Thumb Button (Back)**: Toggle physical mouse control between Cursor 1 and Cursor 2.
- **System Tray Icon**: Right-click the DualPointer icon near your Windows clock to:
  - Toggle **Mouse Side Button** switching
  - Toggle **Landing Ripple Pulse** effect
  - Toggle the click-through **Ghost Pointer** overlay
  - Toggle **Start with Windows** autostart
  - Toggle **Audio Click Feedback** sound
  - Reset saved positions to screen centers
  - Exit

---

## 🎮 The Combined Multi-Screen Workflow

1. Hover over a video thumbnail on YouTube (Monitor 1). The video preview starts, and the blue **`Locked`** badge appears automatically.
2. Press **`Alt + \`** or click your **Mouse Side Button**: Your mouse instantly teleports to Monitor 2 with a quick landing ripple. A distinct ghost cursor remains parked over the YouTube video on Monitor 1.
3. Work, click, scroll, and type on Monitor 2—the YouTube video on Monitor 1 **keeps playing smoothly without stopping**.
4. Press **`Alt + \`** or the side button anytime to instantly return to your exact spot on Monitor 1!

---

## ⚙️ Configuration

Desktop settings are saved automatically in `~/.dualpointer_config.json`:

```json
{
  "hotkey_modifier": "alt",
  "hotkey_key": "\\",
  "ghost_cursor_enabled": true,
  "overlay_size": 44,
  "sound_cues": false,
  "mouse_side_button": "xbutton1",
  "landing_ripple": true
}
```

- **`hotkey_modifier`**: `"alt"`, `"ctrl"`, `"ctrl+alt"`, or `"none"`
- **`hotkey_key`**: `"\\"`, `"c"`, `"f8"`, `"space"`, etc.
- **`mouse_side_button`**: `"xbutton1"` (thumb back), `"xbutton2"` (thumb forward), or `"none"`
- **`landing_ripple`**: `true` / `false` (sonar ring pulse upon cursor teleport)
- **`ghost_cursor_enabled`**: `true` / `false` (display visual parked indicator)
- **`sound_cues`**: `true` / `false` (subtle audio beep on switch)

---

## 🔬 How It Works Internally

### YouTube Hover Lock (Browser)
1. **`world: "MAIN"` Execution**: Runs in the page's main JavaScript context rather than an isolated extension sandbox, giving direct access to DOM prototypes and Custom Elements.
2. **`HTMLMediaElement.prototype.pause` Interception**: Blocks internal calls to `.pause()` on active preview containers while in locked state.
3. **`blur` & `visibilitychange` Suppression**: Suppresses window blur events during the capture phase so YouTube never detects that you moved to another monitor or application.
4. **`MutationObserver` Guard**: Automatically strips `hidden` attributes or `display: none` styles if YouTube attempts to hide the preview player.
5. **250ms Heartbeat & Auto-Loop**: Re-triggers playback and loops the preview when nearing duration end.

### DualPointer (Desktop)
1. **Win32 DPI Awareness v2**: Calls `SetProcessDpiAwareness(2)` for exact coordinate mapping across mixed high-DPI (e.g. 4K 150%) and standard 1080p monitors.
2. **Low-Level Mouse Hook (`WH_MOUSE_LL`)**: Intercepts `WM_XBUTTONUP` to trigger swaps and suppresses the default browser "Back" navigation.
3. **Layered Click-Through Windows**: Ghost cursor and ripple overlays use `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOPMOST` with singleton module-level `WNDPROC` callbacks to achieve zero mouse interference and zero CPU usage at idle.

---

## 🧪 Testing

Run the automated test suite (18 unit tests covering all components):
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
│   ├── ripple_overlay.py        # Visual landing sonar ripple effect
│   ├── mouse_hook.py            # Low-level mouse side-button hook
│   ├── hotkey_manager.py        # Windows RegisterHotKey engine
│   ├── autostart.py             # Windows registry autostart manager
│   ├── config.py                # Configuration management
│   └── requirements.txt         # Desktop dependencies
├── browser-extension/
│   ├── manifest.json            # Manifest V3 extension definition
│   ├── popup.html               # Extension settings popup UI
│   ├── popup.css                # Dark theme glassmorphic styles
│   ├── popup.js                 # Settings persistence & live tab sync
│   ├── content.js               # Main-world event & prototype protection
│   ├── styles.css               # Lock badge styling
│   └── icons/                   # Extension icons
├── userscript/
│   └── youtube-preview-lock.user.js  # Standalone Tampermonkey script
├── tests/
│   ├── test_cursor_manager.py   # Coordinate & bounds tests
│   ├── test_ghost_overlay.py    # Overlay state tests
│   ├── test_ripple_overlay.py   # Landing ripple tests
│   ├── test_mouse_hook.py       # Mouse hook tests
│   ├── test_hotkey_manager.py   # Key parsing tests
│   ├── test_autostart.py        # Autostart tests
│   └── test_config.py           # Configuration tests
├── docs/
│   ├── USAGE.md                 # Detailed user guide
│   └── plans/                   # Architecture & design specs
└── README.md
```

## 📄 License
MIT
