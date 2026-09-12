"""
Cursor State & Coordinate Management for DualPointer.
Handles dual-slot coordinate memory, multi-monitor virtual screen bounds,
and Windows User32 API SetCursorPos/GetCursorPos bindings.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, Callable
import sys
import ctypes
from ctypes import wintypes


@dataclass
class ScreenBounds:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


def get_default_virtual_screen_bounds() -> ScreenBounds:
    """Queries Windows User32 for the combined virtual screen bounding box spanning all monitors."""
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            SM_XVIRTUALSCREEN = 76
            SM_YVIRTUALSCREEN = 77
            SM_CXVIRTUALSCREEN = 78
            SM_CYVIRTUALSCREEN = 79

            left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

            # Fallback if virtual metrics return 0 or invalid dimensions
            if width <= 0 or height <= 0:
                width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                left, top = 0, 0

            return ScreenBounds(left=left, top=top, width=width, height=height)
        except Exception:
            pass

    return ScreenBounds(left=0, top=0, width=1920, height=1080)


def get_physical_cursor_pos() -> Tuple[int, int]:
    """Retrieves current physical cursor position on Windows."""
    if sys.platform == "win32":
        try:
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return int(pt.x), int(pt.y)
        except Exception:
            pass
    return 0, 0


def set_physical_cursor_pos(x: int, y: int) -> bool:
    """Sets system cursor position via Windows SetCursorPos."""
    if sys.platform == "win32":
        try:
            return bool(ctypes.windll.user32.SetCursorPos(int(x), int(y)))
        except Exception:
            pass
    return False


class CursorManager:
    """Manages two cursor slots, coordinate clamping, and switching logic."""

    def __init__(
        self,
        initial_pos_1: Optional[Tuple[int, int]] = None,
        initial_pos_2: Optional[Tuple[int, int]] = None,
        screen_bounds_provider: Optional[Callable[[], ScreenBounds]] = None,
    ):
        self.bounds_provider = screen_bounds_provider or get_default_virtual_screen_bounds
        bounds = self.bounds_provider()

        # Default slot positions if not specified
        center_x = bounds.left + bounds.width // 4
        center_y = bounds.top + bounds.height // 2

        self.slot_1: Tuple[int, int] = initial_pos_1 or (center_x, center_y)
        self.slot_2: Tuple[int, int] = initial_pos_2 or (
            bounds.left + (bounds.width * 3) // 4,
            center_y,
        )

        self.active_slot: int = 1

    @property
    def inactive_slot(self) -> int:
        return 2 if self.active_slot == 1 else 1

    @property
    def active_slot_pos(self) -> Tuple[int, int]:
        return self.slot_1 if self.active_slot == 1 else self.slot_2

    @property
    def inactive_slot_pos(self) -> Tuple[int, int]:
        return self.slot_2 if self.active_slot == 1 else self.slot_1

    def clamp_coordinates(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Clamps coordinate (x, y) within current virtual desktop bounds."""
        bounds = self.bounds_provider()
        x, y = pos

        max_x = bounds.right - 1
        max_y = bounds.bottom - 1

        clamped_x = max(bounds.left, min(x, max_x))
        clamped_y = max(bounds.top, min(y, max_y))
        return clamped_x, clamped_y

    def switch_slot(
        self,
        current_pos: Optional[Tuple[int, int]] = None,
        apply_to_os: bool = False,
    ) -> Tuple[int, int]:
        """
        Saves current position into active slot, swaps active slot,
        and returns the target coordinates for the new active slot.
        If apply_to_os is True, calls SetCursorPos on Windows.
        """
        if current_pos is None:
            current_pos = get_physical_cursor_pos()

        current_pos = self.clamp_coordinates(current_pos)

        if self.active_slot == 1:
            self.slot_1 = current_pos
            self.active_slot = 2
            target_pos = self.slot_2
        else:
            self.slot_2 = current_pos
            self.active_slot = 1
            target_pos = self.slot_1

        target_pos = self.clamp_coordinates(target_pos)

        if apply_to_os:
            set_physical_cursor_pos(target_pos[0], target_pos[1])

        return target_pos
