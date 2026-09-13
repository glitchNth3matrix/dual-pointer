"""
Configuration management for DualPointer.
Handles hotkey preferences, overlay settings, and persistent storage.
"""

import json
import os
from dataclasses import dataclass, asdict


@dataclass
class DualPointerConfig:
    hotkey_modifier: str = "alt"      # e.g. "alt", "ctrl", "ctrl+alt", "none"
    hotkey_key: str = "\\"            # e.g. "\\", "c", "f8", "space"
    ghost_cursor_enabled: bool = True
    overlay_size: int = 44
    sound_cues: bool = False
    mouse_side_button: str = "xbutton1"  # "xbutton1" (back), "xbutton2" (forward), or "none"
    landing_ripple: bool = True          # Visual ripple animation at cursor landing location

    def to_dict(self) -> dict:
        return asdict(self)

    def save_to_file(self, filepath: str) -> None:
        """Saves configuration to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "DualPointerConfig":
        """Loads configuration from JSON file or returns defaults if not found/corrupt."""
        if not os.path.exists(filepath):
            return cls()

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                hotkey_modifier=data.get("hotkey_modifier", "alt"),
                hotkey_key=data.get("hotkey_key", "\\"),
                ghost_cursor_enabled=data.get("ghost_cursor_enabled", True),
                overlay_size=data.get("overlay_size", 44),
                sound_cues=data.get("sound_cues", False),
                mouse_side_button=data.get("mouse_side_button", "xbutton1"),
                landing_ripple=data.get("landing_ripple", True),
            )
        except Exception:
            return cls()
