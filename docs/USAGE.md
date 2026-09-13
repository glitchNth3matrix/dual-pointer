# DualPointer User Guide & Workflow (v1.3)

## Overview
DualPointer enables you to control two independent mouse pointer locations on Windows using a single physical mouse, while keeping video previews on websites like YouTube continuously playing across monitors, window clicks, and application switches.

---

## Step-by-Step Setup

### Step 1: Install or Reload the YouTube Hover Lock Extension
1. In Google Chrome, Microsoft Edge, or Brave, navigate to:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Turn ON **Developer mode** (toggle in top-right corner).
3. Click **Load unpacked** (top-left button) and select the `browser-extension` folder:
   ```text
   ...\dual-pointer\browser-extension
   ```
   *(If already loaded, simply click the **🔄 Reload** icon on the extension card).*
4. Click the extension icon in your browser toolbar to customize settings via the new **Popup Menu**:
   - **Auto-Lock on Hover**: Enable/disable automatic locking.
   - **Hover Delay**: Adjust delay from 200ms to 2000ms.
   - **Auto-Loop Video**: Continuously loop previews.
   - **Auto-Unmute Audio**: Unmute audio immediately when a preview locks.
   - **On-Screen Badge**: Show or hide the status badge.

---

### Step 2: Run the Desktop Dual Cursor Utility
In PowerShell or Command Prompt:

```powershell
python desktop/dual_pointer.py
```

*(Or run silently in the background with `pythonw desktop/dual_pointer.py`).*

Features running automatically:
- **Hotkeys**: Press **`Alt + \`** to switch cursors.
- **Mouse Thumb Button**: Click your mouse side button (Back) for instant switching without moving your hand to the keyboard.
- **Landing Ripple**: An animated cyan/orange sonar ripple marks your new mouse location immediately upon teleporting.
- **Ghost Pointer**: A click-through indicator marks your parked cursor location on the inactive monitor.

---

## Daily Workflow: YouTube Previews across Multiple Screens

1. **Hover on YouTube (Monitor 1)**:
   - Move your cursor over any video card on the YouTube homepage or search page.
   - Within your configured delay (default: 700ms), the preview locks and shows the blue **`[🔒 Locked]`** badge.

2. **Teleport to Monitor 2**:
   - Click your **Mouse Thumb Button** or press **`Alt + \`**.
   - Your cursor instantly snaps to Monitor 2, highlighted by a subtle landing sonar pulse.
   - The YouTube preview on Monitor 1 **keeps playing smoothly without stopping**, even while you click, scroll, and type on Monitor 2!

3. **Return to Monitor 1**:
   - Click the side button or press **`Alt + \`** again.
   - Your cursor lands exactly where you left it on Monitor 1.

4. **Dismissing or Transferring Previews**:
   - Hover over another video to transfer the lock.
   - Press **`Alt + P`**, hit **`Escape`**, or click the blue lock badge to release.

---

## Customizing Preferences

Configuration is saved in `~/.dualpointer_config.json`:

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

- **`mouse_side_button`**: `"xbutton1"` (thumb back), `"xbutton2"` (thumb forward), or `"none"`
- **`landing_ripple`**: `true` / `false` (expand sonar ring upon teleporting)
- **`ghost_cursor_enabled`**: `true` / `false` (show parked cursor indicator)
- **`sound_cues`**: `true` / `false` (auditory pitch confirmation)
