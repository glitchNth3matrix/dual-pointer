# DualPointer

> A lightweight Windows dual-cursor switcher utility paired with a YouTube Hover Lock solution.

## Features
- **Dual Cursor Switching**: Toggle physical mouse control between two saved positions across any monitor with a single hotkey (`Alt + \`).
- **Ghost Cursor Overlay**: Displays an unobtrusive, click-through marker showing where your parked cursor is waiting.
- **YouTube Hover Lock**: Keeps YouTube thumbnail video previews actively playing when your cursor leaves the browser window or jumps to another monitor.
- **Ultra-Lightweight**: Minimal CPU and RAM footprint (<15 MB), zero continuous polling.

## Architecture
- `desktop/`: Python-based Windows tray application utilizing native Win32 User32 APIs.
- `browser-extension/`: Chrome / Edge Manifest V3 extension for YouTube preview locking.
- `userscript/`: Standalone Tampermonkey/Violentmonkey script alternative.

See [docs/plans/2026-09-12-dual-pointer-design.md](docs/plans/2026-09-12-dual-pointer-design.md) for architecture details.
