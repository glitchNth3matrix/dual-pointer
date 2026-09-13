# DualPointer User Guide & Workflow (v1.2)

## Overview
DualPointer enables you to control two independent mouse pointer locations on Windows using a single physical mouse, while keeping video previews on websites like YouTube continuously playing across monitors, window clicks, and application switches.

---

## Step-by-Step Setup

### Step 1: Install the YouTube Hover Lock Extension (One-time)
1. In Google Chrome, Microsoft Edge, or Brave, go to your extensions settings:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Turn ON **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked** (top-left button).
4. Select the `browser-extension` folder in this repository.
5. The extension is now active and running with **Automatic Hover Lock**.

> **Note:** If you already had the extension loaded previously, simply click the **🔄 Reload** button on the extension card in `chrome://extensions`, then refresh any open YouTube tabs.

---

### Step 2: Start the Desktop Dual Cursor Utility
In PowerShell or Command Prompt:

```powershell
python desktop/dual_pointer.py
```

*(Or `pythonw desktop/dual_pointer.py` to run silently in the background without a console window).*

You will see:
- A colored tray icon appear in your notification area (near the clock).
- A subtle, semi-transparent ghost pointer appear at the parked slot position on your screen.

---

## Daily Workflow: Watching YouTube Previews while Working Across Screens

1. **Hover on YouTube (Monitor 1)**:
   - Move your cursor over any video card on the YouTube homepage or search page.
   - The preview will begin playing, and within ~0.7 seconds, a blue **`[🔒 Locked]`** badge will appear in the top-right corner.

2. **Switch to Monitor 2**:
   - Press **`Alt + \`** (the Backslash key above Enter).
   - Your system cursor immediately teleports to Monitor 2.
   - A ghost pointer indicator remains over the YouTube card on Monitor 1.
   - The video preview **continues playing without stopping**, even when you click, type, scroll, or switch applications on Monitor 2!

3. **Switch Back to Monitor 1**:
   - Press **`Alt + \`** again whenever you want to return to Monitor 1.
   - Your cursor returns to the exact location you left it.

4. **Changing or Dismissing Previews**:
   - **Switch to a different video**: Hover your mouse over another video thumbnail for 0.7s; the lock smoothly transfers to the new video.
   - **Release the preview**: Press **`Alt + P`**, press **`Escape`**, or click the blue lock badge to unlock.

---

## Customizing Hotkeys & Preferences

Settings are saved in `~/.dualpointer_config.json` (in your user profile directory `C:\Users\<username>\.dualpointer_config.json`):

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
- **`overlay_size`**: pixel size of the ghost indicator (default: 44)
