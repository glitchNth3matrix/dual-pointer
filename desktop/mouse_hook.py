"""
Global Low-Level Mouse Hook for DualPointer.
Intercepts XBUTTON1 (Back) or XBUTTON2 (Forward) mouse side buttons
to allow instantaneous cursor switching without touching the keyboard.
"""

import sys
import threading
from typing import Callable, Optional

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    WH_MOUSE_LL = 14
    WM_XBUTTONDOWN = 0x020B
    WM_XBUTTONUP = 0x020C
    WM_QUIT = 0x0012

    HOOKPROC = ctypes.WINFUNCTYPE(
        ctypes.c_ssize_t,
        ctypes.c_int,
        wintypes.WPARAM,
        wintypes.LPARAM,
    )

    class MSLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("pt", wintypes.POINT),
            ("mouseData", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong),
        ]

    user32.SetWindowsHookExW.argtypes = [
        ctypes.c_int,
        HOOKPROC,
        wintypes.HINSTANCE,
        wintypes.DWORD,
    ]
    user32.SetWindowsHookExW.restype = wintypes.HHOOK

    user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL

    user32.CallNextHookEx.argtypes = [
        wintypes.HHOOK,
        ctypes.c_int,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.CallNextHookEx.restype = ctypes.c_ssize_t

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    kernel32.GetCurrentThreadId.argtypes = []
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD


class MouseHookManager:
    """Manages low-level mouse hook to capture side button clicks on Windows."""

    def __init__(self, on_trigger: Callable[[], None]):
        self.on_trigger = on_trigger
        self.target_button = "xbutton1"
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._hhook = None
        self._running: bool = False
        self._hook_proc_ref = None

    @property
    def is_running(self) -> bool:
        return self._running and self._hhook is not None

    def start(self, target_button: str = "xbutton1") -> bool:
        """Starts the mouse hook thread for the specified button ('xbutton1', 'xbutton2', or 'none')."""
        self.stop()
        self.target_button = target_button.lower().strip()

        if self.target_button in ("none", "disabled") or sys.platform != "win32":
            return False

        self._running = True
        self._started_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        self._started_event.wait(timeout=2.0)
        return self.is_running

    def _worker(self):
        try:
            self._thread_id = kernel32.GetCurrentThreadId()

            def hook_callback(nCode, wParam, lParam):
                if nCode >= 0 and wParam == WM_XBUTTONUP:
                    hook_struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                    btn_id = (hook_struct.mouseData >> 16) & 0xFFFF

                    matched = (
                        (btn_id == 1 and self.target_button == "xbutton1")
                        or (btn_id == 2 and self.target_button == "xbutton2")
                    )

                    if matched:
                        try:
                            self.on_trigger()
                        except Exception:
                            pass
                        # Return 1 to suppress the default browser back/forward action
                        return 1

                return user32.CallNextHookEx(self._hhook, nCode, wParam, lParam)

            # Retain reference to callback to avoid garbage collection
            self._hook_proc_ref = HOOKPROC(hook_callback)
            hinst = kernel32.GetModuleHandleW(None)

            self._hhook = user32.SetWindowsHookExW(
                WH_MOUSE_LL,
                self._hook_proc_ref,
                hinst,
                0,
            )

            self._started_event.set()

            if not self._hhook:
                self._running = False
                return

            msg = wintypes.MSG()
            while self._running:
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0 or msg.message == WM_QUIT:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        except Exception:
            pass
        finally:
            if self._hhook and sys.platform == "win32":
                user32.UnhookWindowsHookEx(self._hhook)
                self._hhook = None
            self._started_event.set()

    def stop(self):
        """Removes the mouse hook and stops the thread."""
        self._running = False
        if sys.platform == "win32" and self._thread_id:
            try:
                user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        self._thread_id = None
        self._hhook = None
