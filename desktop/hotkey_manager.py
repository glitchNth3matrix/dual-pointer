"""
Global Hotkey Engine for Windows.
Uses native Windows User32 RegisterHotKey / UnregisterHotKey API,
ensuring zero CPU polling and maximum compatibility without third-party drivers.
"""

import sys
import threading
from typing import Callable, Tuple, Optional


def parse_hotkey_string(modifier_str: str, key_str: str) -> Tuple[int, int]:
    """
    Parses human-friendly modifier and key strings into Windows (modifiers_flag, virtual_key_code).
    """
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008
    MOD_NOREPEAT = 0x4000

    mod = MOD_NOREPEAT
    m_lower = modifier_str.lower()
    if "alt" in m_lower:
        mod |= MOD_ALT
    if "ctrl" in m_lower or "control" in m_lower:
        mod |= MOD_CONTROL
    if "shift" in m_lower:
        mod |= MOD_SHIFT
    if "win" in m_lower or "super" in m_lower:
        mod |= MOD_WIN

    k_lower = key_str.lower().strip()

    # Common Windows Virtual Key Codes
    vk_map = {
        "\\": 0xDC,       # VK_OEM_5 (Backslash / pipe)
        "backslash": 0xDC,
        "/": 0xBF,        # VK_OEM_2
        "`": 0xC0,        # VK_OEM_3 (Backtick / tilde)
        "tab": 0x09,
        "space": 0x20,
        "f1": 0x70,
        "f2": 0x71,
        "f3": 0x72,
        "f4": 0x73,
        "f5": 0x74,
        "f6": 0x75,
        "f7": 0x76,
        "f8": 0x77,
        "f9": 0x78,
        "f10": 0x79,
        "f11": 0x7A,
        "f12": 0x7B,
    }

    if k_lower in vk_map:
        vk = vk_map[k_lower]
    elif len(k_lower) == 1 and ("a" <= k_lower <= "z"):
        vk = ord(k_lower.upper())
    elif len(k_lower) == 1 and ("0" <= k_lower <= "9"):
        vk = ord(k_lower)
    else:
        # Default fallback to VK_OEM_5 (\)
        vk = 0xDC

    return mod, vk


class HotkeyManager:
    """Manages global hotkey registration and thread event dispatch on Windows."""

    HOTKEY_ID = 1001

    def __init__(self, on_trigger: Callable[[], None]):
        self.on_trigger = on_trigger
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._running: bool = False
        self._modifier: str = "alt"
        self._key: str = "\\"

    def start(self, modifier: str = "alt", key: str = "\\") -> bool:
        """Starts the hotkey listener thread."""
        self.stop()
        self._modifier = modifier
        self._key = key

        if sys.platform != "win32":
            return False

        self._running = True
        self._started_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        self._started_event.wait(timeout=2.0)
        return True

    def _worker(self):
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            self._thread_id = kernel32.GetCurrentThreadId()
            mod, vk = parse_hotkey_string(self._modifier, self._key)

            # Register thread-level hotkey (NULL hwnd)
            success = user32.RegisterHotKey(None, self.HOTKEY_ID, mod, vk)
            self._started_event.set()

            if not success:
                return

            msg = wintypes.MSG()
            while self._running:
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0:
                    break

                if msg.message == 0x0312:  # WM_HOTKEY
                    if msg.wParam == self.HOTKEY_ID:
                        try:
                            self.on_trigger()
                        except Exception:
                            pass

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

            user32.UnregisterHotKey(None, self.HOTKEY_ID)
        except Exception:
            pass

    def stop(self):
        """Unregisters the hotkey and terminates the worker thread."""
        self._running = False
        if sys.platform == "win32" and self._thread_id:
            try:
                import ctypes
                WM_QUIT = 0x0012
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        self._thread_id = None
