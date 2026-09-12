"""
DualPointer - Windows Multi-Monitor Dual Cursor Switcher.
Main entry point and system tray controller.
"""

import sys
import os
import time
from typing import Optional
from PIL import Image, ImageDraw

from desktop.config import DualPointerConfig
from desktop.cursor_manager import (
    CursorManager,
    get_physical_cursor_pos,
    get_default_virtual_screen_bounds,
)
from desktop.ghost_overlay import GhostOverlay
from desktop.hotkey_manager import HotkeyManager

CONFIG_FILE = os.path.expanduser("~/.dualpointer_config.json")


def create_tray_icon_image(active_slot: int = 1) -> Image.Image:
    """Generates a 64x64 system tray icon depicting two cursors."""
    img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer rounded background
    draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill=(30, 35, 45, 240))

    # Dot 1 (Cyan / Slot 1)
    color1 = (0, 210, 255, 255) if active_slot == 1 else (100, 110, 130, 200)
    draw.ellipse([12, 22, 28, 38], fill=color1)

    # Dot 2 (Orange / Slot 2)
    color2 = (255, 140, 0, 255) if active_slot == 2 else (100, 110, 130, 200)
    draw.ellipse([36, 22, 52, 38], fill=color2)

    # Accent underline for active slot
    if active_slot == 1:
        draw.line([12, 44, 28, 44], fill=color1, width=3)
    else:
        draw.line([36, 44, 52, 44], fill=color2, width=3)

    return img


class DualPointerApp:
    def __init__(self, config_path: str = CONFIG_FILE):
        self.config_path = config_path
        self.config = DualPointerConfig.load_from_file(config_path)

        self.cursor_manager = CursorManager()
        self.ghost_overlay = GhostOverlay(
            enabled=self.config.ghost_cursor_enabled,
            size=self.config.overlay_size,
        )
        self.hotkey_manager = HotkeyManager(on_trigger=self.toggle_cursor_slot)
        self._tray_icon = None

    def toggle_cursor_slot(self):
        """Action performed when the global hotkey is pressed."""
        # 1. Switch slot and teleport cursor in OS
        target_pos = self.cursor_manager.switch_slot(apply_to_os=True)

        # 2. Update ghost overlay at the parked position
        parked_pos = self.cursor_manager.inactive_slot_pos
        self.ghost_overlay.show(
            parked_pos[0],
            parked_pos[1],
            slot_num=self.cursor_manager.inactive_slot,
        )

        # 3. Optional audio feedback
        if self.config.sound_cues and sys.platform == "win32":
            try:
                import winsound
                freq = 800 if self.cursor_manager.active_slot == 1 else 1100
                winsound.Beep(freq, 60)
            except Exception:
                pass

        # 4. Update tray icon
        if self._tray_icon:
            self._tray_icon.icon = create_tray_icon_image(self.cursor_manager.active_slot)
            self._tray_icon.title = (
                f"DualPointer: Active Slot {self.cursor_manager.active_slot} "
                f"({self.config.hotkey_modifier}+{self.config.hotkey_key})"
            )

    def toggle_ghost_overlay(self, item=None):
        new_val = not self.config.ghost_cursor_enabled
        self.config.ghost_cursor_enabled = new_val
        self.ghost_overlay.set_enabled(new_val)
        if new_val:
            parked_pos = self.cursor_manager.inactive_slot_pos
            self.ghost_overlay.show(parked_pos[0], parked_pos[1], self.cursor_manager.inactive_slot)
        self.config.save_to_file(self.config_path)

    def toggle_sound(self, item=None):
        self.config.sound_cues = not self.config.sound_cues
        self.config.save_to_file(self.config_path)

    def reset_positions(self, item=None):
        bounds = get_default_virtual_screen_bounds()
        center_y = bounds.top + bounds.height // 2
        self.cursor_manager.slot_1 = (bounds.left + bounds.width // 4, center_y)
        self.cursor_manager.slot_2 = (bounds.left + (bounds.width * 3) // 4, center_y)
        parked_pos = self.cursor_manager.inactive_slot_pos
        self.ghost_overlay.show(parked_pos[0], parked_pos[1], self.cursor_manager.inactive_slot)

    def quit_app(self, item=None):
        self.ghost_overlay.stop()
        self.hotkey_manager.stop()
        if self._tray_icon:
            self._tray_icon.stop()

    def run(self):
        """Starts hotkey listener and system tray event loop."""
        self.hotkey_manager.start(
            modifier=self.config.hotkey_modifier,
            key=self.config.hotkey_key,
        )

        try:
            import pystray
            from pystray import MenuItem as item

            menu = pystray.Menu(
                item(
                    lambda text: f"Switch Cursor ({self.config.hotkey_modifier.upper()}+{self.config.hotkey_key.upper()})",
                    lambda: self.toggle_cursor_slot(),
                    default=True,
                ),
                pystray.Menu.SEPARATOR,
                item(
                    "Show Parked Ghost Pointer",
                    self.toggle_ghost_overlay,
                    checked=lambda item: self.config.ghost_cursor_enabled,
                ),
                item(
                    "Audio Click Feedback",
                    self.toggle_sound,
                    checked=lambda item: self.config.sound_cues,
                ),
                item("Reset Saved Positions", self.reset_positions),
                pystray.Menu.SEPARATOR,
                item("Exit", self.quit_app),
            )

            self._tray_icon = pystray.Icon(
                "DualPointer",
                create_tray_icon_image(1),
                f"DualPointer: Active Slot 1 ({self.config.hotkey_modifier}+{self.config.hotkey_key})",
                menu=menu,
            )

            print(f"DualPointer running. Press {self.config.hotkey_modifier}+{self.config.hotkey_key} to toggle cursors.")
            self._tray_icon.run()

        except ImportError:
            print("pystray not installed; running in console mode. Press Ctrl+C to exit.")
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                self.quit_app()


if __name__ == "__main__":
    app = DualPointerApp()
    app.run()
