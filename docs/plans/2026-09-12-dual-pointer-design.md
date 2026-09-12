# DualPointer: Multi-Monitor Dual Cursor & YouTube Preview Lock

## Overview
A lightweight Windows dual-cursor switcher paired with a zero-overhead YouTube preview hover-lock solution. This enables users to park one cursor on a YouTube video card (keeping the inline preview actively playing) while seamlessly switching the physical mouse control to another monitor or application with a quick keystroke.

---

## 1. Requirements & Goals

### Functional Requirements
1. **Cursor State Switching**:
   - Save current cursor coordinates `(x, y)` to the active slot (Slot 1 or Slot 2).
   - Teleport system cursor to the target slot instantly on global hotkey trigger (default: `Alt + \` or `F8`).
   - Support multi-monitor coordinate virtual desktop space (negative coordinates, multi-DPI, differing resolutions).
2. **Ghost Pointer Overlay**:
   - Render a transparent, click-through overlay window showing the parked location of the inactive cursor.
   - Distinct visual cues (semi-transparent arrow with slot number "1" or "2" badge).
   - 0% click interception: all clicks pass through to underlying applications (`WS_EX_TRANSPARENT | WS_EX_LAYERED`).
3. **YouTube Preview Hover Lock**:
   - Keep YouTube thumbnail inline preview video playing when the cursor leaves the window or moves to another monitor.
   - Support toggle-lock via hotkey (`Alt + P`), middle-click, or automatic hover-lock.
   - Clean unlock on click or navigation.
   - Available as both a Manifest V3 browser extension (Chrome / Edge / Brave) and a standalone Userscript (.user.js).
4. **Efficiency**:
   - Minimal memory footprint (<20 MB RAM for desktop app, near-zero for browser extension).
   - Zero polling loops: purely event-driven architecture with 0% CPU consumption when idle.

---

## 2. Architecture & Components

### Component A: Desktop Switcher (`desktop/`)
* **`dual_pointer.py`**: Application bootstrap, system tray icon (`pystray`), global hotkey bindings (`keyboard`), and lifecycle management.
* **`cursor_manager.py`**: Interacts with Windows User32 API (`GetCursorPos`, `SetCursorPos`, `GetSystemMetrics`) to manage Slot 1 and Slot 2 coordinates.
* **`ghost_overlay.py`**: High-performance Win32 layered click-through window displaying the parked ghost pointer.
* **`config.py`**: Configuration options for custom hotkeys, sound notifications, and overlay appearance.

### Component B: YouTube Hover Lock (`browser-extension/` & `userscript/`)
* **`manifest.json`**: Chrome/Edge Manifest V3 definition targeting `*://*.youtube.com/*`.
* **`content.js`**:
  * Intercepts `mouseleave`, `mouseout`, and `pointerleave` events on `#mouseover-overlay` and `ytd-rich-item-renderer`.
  * Maintains the active preview player element in DOM and prevents YouTube's tear-down handlers from triggering on pointer exit.
  * Adds an unobtrusive lock badge to the video corner to indicate pinned preview status.
* **`youtube-preview-lock.user.js`**: Standalone single-file script for users of Tampermonkey/Violentmonkey.

---

## 3. Data Flow
1. User positions cursor over YouTube thumbnail on Monitor 1. Preview starts playing.
2. User presses `Alt + P` (or auto-lock engages): YouTube preview lock pins the active player.
3. User presses `Alt + \`:
   - `desktop` app records Slot 1 position `(x1, y1)`.
   - `desktop` app activates Slot 2 and calls `SetCursorPos(x2, y2)`.
   - Ghost overlay displays pointer at `(x1, y1)` on Monitor 1.
   - Physical mouse now drives cursor on Monitor 2.
4. User works on Monitor 2; YouTube preview on Monitor 1 continues uninterrupted.
5. User presses `Alt + \` again: cursor teleports back to `(x1, y1)`.

---

## 4. Verification & Testing Plan
1. **Desktop App**:
   - Test hotkey swapping between 2 distinct coordinates.
   - Verify click-through behavior on the ghost cursor (clicks register on apps behind it).
   - Verify multi-monitor coordinate clamping and edge cases.
   - Verify 0% idle CPU and clean shutdown from tray.
2. **Browser Extension**:
   - Load unpacked extension into Chrome/Edge.
   - Navigate to youtube.com, hover over video card, trigger lock, move mouse out of browser window.
   - Confirm video preview stays alive.
   - Confirm clean unlock when clicking another video or pressing unlock key.
