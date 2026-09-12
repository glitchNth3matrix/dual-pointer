# DualPointer & YouTube Hover Lock Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Windows dual-cursor switcher utility (`DualPointer`) with ghost pointer overlay and a companion YouTube Hover Lock browser extension/userscript to keep inline previews playing across monitors.

**Architecture:** The desktop component is a modular Python Win32 system tray application managing two cursor coordinate slots and a click-through layered transparent ghost cursor overlay. The browser component is a lightweight Manifest V3 extension and standalone userscript that intercepts mouse-leave/pointer-leave events on YouTube video cards.

**Tech Stack:** Python 3 (ctypes, pywin32, pystray, keyboard, Pillow), Windows User32 API, JavaScript (Chrome Manifest V3 / Userscript standard DOM API), pytest.

---

### Task 1: Repository Setup and Git Configuration

**Files:**
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Write `.gitignore`**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS / Editor
.DS_Store
Thumbs.db
.vscode/
.idea/
```

**Step 2: Write initial `README.md`**
Overview of DualPointer, feature summary, quick start guide.

**Step 3: Commit files**
```bash
git add .gitignore README.md
git commit -m "chore: initialize repository with gitignore and README"
```

---

### Task 2: Desktop Cursor Manager & Coordinate Engine

**Files:**
- Create: `desktop/cursor_manager.py`
- Test: `tests/test_cursor_manager.py`

**Step 1: Write failing test for CursorManager**
```python
import pytest
from desktop.cursor_manager import CursorManager

def test_cursor_slots_initialization():
    manager = CursorManager(initial_pos_1=(100, 100), initial_pos_2=(500, 500))
    assert manager.active_slot == 1
    assert manager.slot_1 == (100, 100)
    assert manager.slot_2 == (500, 500)

def test_switch_slot():
    manager = CursorManager(initial_pos_1=(100, 100), initial_pos_2=(500, 500))
    # When active is 1, switching with current pos (150, 150) should update slot 1 and return slot 2
    target_pos = manager.switch_slot(current_pos=(150, 150))
    assert manager.active_slot == 2
    assert manager.slot_1 == (150, 150)
    assert target_pos == (500, 500)
    assert manager.inactive_slot_pos == (150, 150)
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_cursor_manager.py`
Expected: ModuleNotFoundError / FAIL

**Step 3: Implement `desktop/cursor_manager.py`**
Implement `CursorManager` supporting:
- Dual-slot state tracking
- Virtual screen bounds detection via `GetSystemMetrics(SM_XVIRTUALSCREEN)`
- Coordinate clamping to prevent cursor from getting lost off-screen
- Safe Win32 `GetCursorPos` and `SetCursorPos` wrappers

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_cursor_manager.py`
Expected: PASS

**Step 5: Commit**
```bash
git add desktop/cursor_manager.py tests/test_cursor_manager.py
git commit -m "feat(desktop): implement cursor state manager and tests"
```

---

### Task 3: Ghost Pointer Click-Through Overlay Window

**Files:**
- Create: `desktop/ghost_overlay.py`
- Test: `tests/test_ghost_overlay.py`

**Step 1: Write unit tests for overlay positioning & styling logic**
Test coordinate translation, icon generation, and state toggle handlers.

**Step 2: Implement `desktop/ghost_overlay.py`**
- Win32 layered click-through window using `tkinter` or raw `ctypes` User32.
- Configure `GWL_EXSTYLE` with `WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_TOPMOST`.
- Render a distinct cursor indicator (semi-transparent pointer with slot badge).
- Methods: `show(x, y, slot_num)`, `hide()`, `destroy()`.

**Step 3: Verify overlay behavior & run tests**
Verify window creation, position updates, and transparency style masks.

**Step 4: Commit**
```bash
git add desktop/ghost_overlay.py tests/test_ghost_overlay.py
git commit -m "feat(desktop): implement click-through ghost pointer overlay"
```

---

### Task 4: Configuration & Main Desktop Application (Tray & Hotkey)

**Files:**
- Create: `desktop/config.py`
- Create: `desktop/dual_pointer.py`
- Create: `desktop/requirements.txt`

**Step 1: Create `desktop/config.py`**
Defaults for hotkey (`alt+\`), ghost cursor color/size, sound cues (optional toggle).

**Step 2: Implement `desktop/dual_pointer.py`**
- Global hotkey listener registering the switch key.
- Pystray system tray icon with menu (Switch Slot, Toggle Ghost Cursor, Hotkey Settings, Exit).
- Graceful shutdown handlers.

**Step 3: Test configuration loading and hotkey registration**
Run: `python -m pytest tests/`

**Step 4: Commit**
```bash
git add desktop/config.py desktop/dual_pointer.py desktop/requirements.txt
git commit -m "feat(desktop): complete main tray application and hotkey engine"
```

---

### Task 5: YouTube Hover Lock Browser Extension (Manifest V3)

**Files:**
- Create: `browser-extension/manifest.json`
- Create: `browser-extension/content.js`
- Create: `browser-extension/styles.css`
- Create: `browser-extension/icons/icon48.png`

**Step 1: Create `manifest.json`**
Define extension permissions and content script matching `https://*.youtube.com/*`.

**Step 2: Create `content.js`**
- Listen for hover over video cards (`ytd-rich-item-renderer`, `ytd-video-preview`).
- Intercept and stop propagation of `pointerleave`, `mouseleave`, `mouseout` on locked card.
- Global shortcut listener (`Alt + P` or middle-click) to toggle lock on active preview.
- Visual badge showing "Preview Locked (Alt+P to unlock)".

**Step 3: Create `styles.css`**
Badge styling and pinned indicator animation.

**Step 4: Commit**
```bash
git add browser-extension/
git commit -m "feat(extension): add YouTube Hover Lock Manifest V3 extension"
```

---

### Task 6: Standalone Userscript

**Files:**
- Create: `userscript/youtube-preview-lock.user.js`

**Step 1: Write standalone userscript**
Package the hover-lock logic with Tampermonkey/Violentmonkey headers for 1-click install.

**Step 2: Verify userscript metadata and linting**

**Step 3: Commit**
```bash
git add userscript/
git commit -m "feat(userscript): add standalone userscript for Tampermonkey"
```

---

### Task 7: Full Integration Documentation & Verification

**Files:**
- Update: `README.md`
- Create: `docs/USAGE.md`

**Step 1: Complete setup & usage guide**
Detail installation steps for both desktop app and browser extension, including how to test with YouTube.

**Step 2: Commit and tag initial release**
```bash
git add README.md docs/USAGE.md
git commit -m "docs: complete setup, usage guide, and verification steps"
```
