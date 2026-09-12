# DualPointer User Guide & Workflow

## Overview
DualPointer allows you to manage two mouse positions on Windows with a single physical mouse, while keeping inline previews on websites like YouTube alive when your mouse is elsewhere.

---

## Step-by-Step Setup

### Step 1: Start the Desktop Utility
Open PowerShell or Command Prompt in the repository folder:

```powershell
python desktop/dual_pointer.py
```

You will see:
```text
DualPointer running. Press alt+\ to toggle cursors.
```
And a small tray icon with two colored dots will appear in your Windows notification area (near the clock).

### Step 2: Install the YouTube Extension (One-time)
1. In Google Chrome or Microsoft Edge, go to the extensions manager:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Turn ON **Developer mode**.
3. Click **Load unpacked**.
4. Browse to and select:
   `c:\Users\Shadow\Documents\antigravity\beautiful-hawking\browser-extension`
5. The "YouTube Hover Lock" extension is now active.

---

## Daily Workflow: Watching YouTube Previews while Working

1. **Park on YouTube (Monitor 1)**:
   - Open YouTube homepage or search results.
   - Hover your cursor over the video card you want to watch. The inline preview will begin playing.
   - Press **`Alt + P`** (or click the small lock badge).
   - A blue indicator badge `[🔒 Locked (Alt+P to unlock)]` confirms the preview is pinned.

2. **Switch to Monitor 2**:
   - Press **`Alt + \`** (the Backslash key above Enter).
   - Your cursor instantly jumps to Monitor 2!
   - On Monitor 1, a subtle semi-transparent ghost cursor remains parked at the YouTube video.
   - The YouTube preview continues playing without pausing or disappearing!

3. **Switch Back to Monitor 1**:
   - Press **`Alt + \`** again whenever you want to return to Monitor 1.
   - Your cursor returns to the exact location you left it.

4. **Dismissing / Unlocking**:
   - To stop the preview, press **`Alt + P`** or click the lock badge, or simply click another video to navigate.

---

## Customizing Hotkeys

If you want to use a different key combination (such as `F8` or `Ctrl + Alt + C`):
Edit `~/.dualpointer_config.json` (in your user profile directory `C:\Users\<username>\.dualpointer_config.json`):

```json
{
  "hotkey_modifier": "none",
  "hotkey_key": "f8",
  "ghost_cursor_enabled": true,
  "overlay_size": 40,
  "sound_cues": true
}
```
Restart DualPointer for the changes to take effect.
