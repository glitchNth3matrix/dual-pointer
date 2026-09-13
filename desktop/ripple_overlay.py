"""
Landing Ripple Overlay for DualPointer.
Displays a brief, expanding circular sonar/ripple pulse at the new active cursor position
so you instantly locate your mouse upon switching monitors.
"""

import sys
import threading
import queue
import time
from typing import Optional

_GLOBAL_RIPPLE_OVERLAYS = {}
_RIPPLE_WNDPROC_FUNC = None
_RIPPLE_CLASS_REGISTERED = False

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    WS_POPUP = 0x80000000
    WS_EX_TOPMOST = 0x00000008
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_NOACTIVATE = 0x08000000

    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    HWND_TOPMOST = -1
    SW_HIDE = 0
    COLOR_KEY = 0x00000000  # Black color key

    WNDPROC = ctypes.WINFUNCTYPE(
        ctypes.c_ssize_t,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    )

    user32.DefWindowProcW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.DefWindowProcW.restype = ctypes.c_ssize_t

    user32.CreateWindowExW.restype = wintypes.HWND
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        wintypes.HANDLE,
        wintypes.HINSTANCE,
        wintypes.LPVOID,
    ]

    user32.SetWindowPos.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]

    user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
    user32.SetLayeredWindowAttributes.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        wintypes.BYTE,
        wintypes.DWORD,
    ]

    class PAINTSTRUCT(ctypes.Structure):
        _fields_ = [
            ("hdc", wintypes.HDC),
            ("fErase", wintypes.BOOL),
            ("rcPaint", wintypes.RECT),
            ("fRestore", wintypes.BOOL),
            ("fIncUpdate", wintypes.BOOL),
            ("rgbReserved", ctypes.c_byte * 32),
        ]

    user32.DestroyWindow.restype = wintypes.BOOL
    user32.DestroyWindow.argtypes = [wintypes.HWND]

    user32.ShowWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]

    user32.InvalidateRect.restype = wintypes.BOOL
    user32.InvalidateRect.argtypes = [wintypes.HWND, ctypes.c_void_p, wintypes.BOOL]

    user32.PeekMessageW.restype = wintypes.BOOL
    user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]

    user32.TranslateMessage.restype = wintypes.BOOL
    user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]

    user32.DispatchMessageW.restype = ctypes.c_ssize_t
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]

    user32.BeginPaint.restype = wintypes.HDC
    user32.BeginPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]

    user32.EndPaint.restype = wintypes.BOOL
    user32.EndPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]

    user32.FillRect.restype = ctypes.c_int
    user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HANDLE]

    gdi32.CreateSolidBrush.restype = wintypes.HANDLE
    gdi32.CreateSolidBrush.argtypes = [wintypes.DWORD]

    gdi32.CreatePen.restype = wintypes.HANDLE
    gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.DWORD]

    gdi32.SelectObject.restype = wintypes.HANDLE
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]

    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteObject.argtypes = [wintypes.HANDLE]

    gdi32.Ellipse.restype = wintypes.BOOL
    gdi32.Ellipse.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    gdi32.GetStockObject.restype = wintypes.HANDLE
    gdi32.GetStockObject.argtypes = [ctypes.c_int]

    class WNDCLASSEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HANDLE),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HANDLE),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
            ("hIconSm", wintypes.HANDLE),
        ]

    user32.RegisterClassExW.restype = wintypes.ATOM
    user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEX)]

    def _global_ripple_wndproc(hwnd, msg, wparam, lparam):
        overlay = _GLOBAL_RIPPLE_OVERLAYS.get(hwnd)
        if msg == 0x000F and overlay:  # WM_PAINT
            ps = PAINTSTRUCT()
            hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))

            rect = wintypes.RECT(0, 0, overlay.size, overlay.size)
            bg_brush = gdi32.CreateSolidBrush(COLOR_KEY)
            user32.FillRect(hdc, ctypes.byref(rect), bg_brush)
            gdi32.DeleteObject(bg_brush)

            r = overlay._current_radius
            cx, cy = overlay.size // 2, overlay.size // 2
            pen = gdi32.CreatePen(0, 3, overlay._current_color)
            null_brush = gdi32.GetStockObject(5)  # NULL_BRUSH

            old_pen = gdi32.SelectObject(hdc, pen)
            old_brush = gdi32.SelectObject(hdc, null_brush)

            gdi32.Ellipse(hdc, cx - r, cy - r, cx + r, cy + r)

            gdi32.SelectObject(hdc, old_pen)
            gdi32.SelectObject(hdc, old_brush)
            gdi32.DeleteObject(pen)

            user32.EndPaint(hwnd, ctypes.byref(ps))
            return 0
        elif msg == 0x0002:  # WM_DESTROY
            _GLOBAL_RIPPLE_OVERLAYS.pop(hwnd, None)
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    _RIPPLE_WNDPROC_FUNC = WNDPROC(_global_ripple_wndproc)


class LandingRippleOverlay:
    """Manages the brief landing animation at the destination cursor position."""

    def __init__(self, enabled: bool = True, size: int = 80):
        self.enabled = enabled
        self.size = size
        self._current_radius = 20
        self._current_color = 0x00D0FF00
        self._thread: Optional[threading.Thread] = None
        self._cmd_queue: queue.Queue = queue.Queue()
        self._running: bool = False
        self._hwnd = None
        self._started_event = threading.Event()

        if sys.platform == "win32" and self.enabled:
            self._start_thread()

    def _start_thread(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        self._started_event.wait(timeout=2.0)

    def _worker(self):
        global _RIPPLE_CLASS_REGISTERED
        try:
            hinst = kernel32.GetModuleHandleW(None)
            class_name = "DualPointerRippleOverlaySingleton"

            if not _RIPPLE_CLASS_REGISTERED:
                wce = WNDCLASSEX()
                wce.cbSize = ctypes.sizeof(WNDCLASSEX)
                wce.style = 3
                wce.lpfnWndProc = _RIPPLE_WNDPROC_FUNC
                wce.hInstance = hinst
                wce.lpszClassName = class_name
                user32.RegisterClassExW(ctypes.byref(wce))
                _RIPPLE_CLASS_REGISTERED = True

            ex_style = (
                WS_EX_TOPMOST
                | WS_EX_TOOLWINDOW
                | WS_EX_LAYERED
                | WS_EX_TRANSPARENT
                | WS_EX_NOACTIVATE
            )

            hwnd = user32.CreateWindowExW(
                ex_style,
                class_name,
                "DualPointerRipple",
                WS_POPUP,
                0,
                0,
                self.size,
                self.size,
                None,
                None,
                hinst,
                None,
            )

            user32.SetLayeredWindowAttributes(hwnd, COLOR_KEY, 220, 1 | 2)  # LWA_COLORKEY | LWA_ALPHA
            self._hwnd = hwnd
            _GLOBAL_RIPPLE_OVERLAYS[hwnd] = self
            self._started_event.set()

            msg = wintypes.MSG()
            while self._running:
                try:
                    while True:
                        cmd, args = self._cmd_queue.get_nowait()
                        if cmd == "PULSE":
                            x, y, color = args
                            self._current_color = color
                            half = self.size // 2
                            user32.SetWindowPos(
                                hwnd,
                                HWND_TOPMOST,
                                x - half,
                                y - half,
                                self.size,
                                self.size,
                                SWP_NOACTIVATE | SWP_SHOWWINDOW,
                            )
                            # Animate expanding ring
                            for radius in (12, 18, 26, 34):
                                self._current_radius = radius
                                user32.InvalidateRect(hwnd, None, True)
                                time.sleep(0.04)
                            user32.ShowWindow(hwnd, SW_HIDE)
                        elif cmd == "STOP":
                            self._running = False
                            _GLOBAL_RIPPLE_OVERLAYS.pop(hwnd, None)
                            user32.DestroyWindow(hwnd)
                            break
                        self._cmd_queue.task_done()
                except queue.Empty:
                    pass

                while user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                    if msg.message == 0x0012:
                        self._running = False
                        break
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))

                time.sleep(0.01)

        except Exception:
            self._started_event.set()

    def pulse(self, x: int, y: int, slot_num: int = 1):
        """Displays an expanding pulse ripple at (x, y)."""
        if not self.enabled or not self._running:
            return
        color = 0x00D0FF00 if slot_num == 1 else 0x0000A5FF
        self._cmd_queue.put(("PULSE", (x, y, color)))

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if enabled and not self._running and sys.platform == "win32":
            self._start_thread()

    def stop(self):
        self._running = False
        self._cmd_queue.put(("STOP", None))
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.8)
