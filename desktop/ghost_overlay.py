"""
Ghost Pointer Overlay for DualPointer.
Creates a high-performance, layered, click-through window (WS_EX_TRANSPARENT | WS_EX_LAYERED)
at the coordinates of the parked/inactive cursor.
"""

import sys
import threading
import queue
import time
from typing import Tuple, Optional

_GLOBAL_OVERLAYS = {}
_WNDPROC_FUNC = None
_CLASS_REGISTERED = False

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

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

    user32.DrawTextW.restype = ctypes.c_int
    user32.DrawTextW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int, ctypes.c_void_p, wintypes.UINT]

    gdi32.CreateSolidBrush.restype = wintypes.HANDLE
    gdi32.CreateSolidBrush.argtypes = [wintypes.DWORD]

    gdi32.CreatePen.restype = wintypes.HANDLE
    gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.DWORD]

    gdi32.SelectObject.restype = wintypes.HANDLE
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]

    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteObject.argtypes = [wintypes.HANDLE]

    gdi32.Polygon.restype = wintypes.BOOL
    gdi32.Polygon.argtypes = [wintypes.HDC, ctypes.c_void_p, ctypes.c_int]

    gdi32.Ellipse.restype = wintypes.BOOL
    gdi32.Ellipse.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    gdi32.SetBkMode.restype = ctypes.c_int
    gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]

    gdi32.SetTextColor.restype = wintypes.DWORD
    gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.DWORD]

    COLOR_KEY = 0x00FF00FF  # Magenta transparent key

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def _global_wnd_proc(hwnd, msg, wparam, lparam):
        overlay = _GLOBAL_OVERLAYS.get(hwnd)
        if msg == 0x000F and overlay:  # WM_PAINT
            ps = PAINTSTRUCT()
            hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))

            rect = wintypes.RECT(0, 0, overlay.size, overlay.size)
            bg_brush = gdi32.CreateSolidBrush(COLOR_KEY)
            user32.FillRect(hdc, ctypes.byref(rect), bg_brush)
            gdi32.DeleteObject(bg_brush)

            badge_color = 0x00D08000 if overlay.current_slot == 1 else 0x002080FF
            badge_brush = gdi32.CreateSolidBrush(badge_color)
            white_brush = gdi32.CreateSolidBrush(0x00FFFFFF)
            black_pen = gdi32.CreatePen(0, 2, 0x00000000)

            old_brush = gdi32.SelectObject(hdc, white_brush)
            old_pen = gdi32.SelectObject(hdc, black_pen)

            pts = (POINT * 7)(
                POINT(0, 0),
                POINT(0, 22),
                POINT(6, 17),
                POINT(11, 26),
                POINT(15, 24),
                POINT(10, 15),
                POINT(17, 15),
            )
            gdi32.Polygon(hdc, pts, 7)

            gdi32.SelectObject(hdc, badge_brush)
            gdi32.Ellipse(hdc, 16, 16, 38, 38)

            gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
            gdi32.SetTextColor(hdc, 0x00FFFFFF)
            text = str(overlay.current_slot)
            badge_rect = wintypes.RECT(16, 16, 38, 38)
            user32.DrawTextW(
                hdc,
                text,
                len(text),
                ctypes.byref(badge_rect),
                0x00000001 | 0x00000004 | 0x00000020,
            )

            gdi32.SelectObject(hdc, old_brush)
            gdi32.SelectObject(hdc, old_pen)
            gdi32.DeleteObject(badge_brush)
            gdi32.DeleteObject(white_brush)
            gdi32.DeleteObject(black_pen)

            user32.EndPaint(hwnd, ctypes.byref(ps))
            return 0
        elif msg == 0x0002:  # WM_DESTROY
            _GLOBAL_OVERLAYS.pop(hwnd, None)
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    _WNDPROC_FUNC = WNDPROC(_global_wnd_proc)


class GhostOverlay:
    """Manages the visual indicator for the parked cursor."""

    def __init__(self, enabled: bool = True, size: int = 44):
        self.enabled = enabled
        self.size = size
        self.is_visible = False
        self.current_pos: Tuple[int, int] = (0, 0)
        self.current_slot: int = 1

        self._thread: Optional[threading.Thread] = None
        self._cmd_queue: queue.Queue = queue.Queue()
        self._hwnd = None
        self._running = False
        self._started_event = threading.Event()

        if sys.platform == "win32" and self.enabled:
            self._start_overlay_thread()

    def _start_overlay_thread(self):
        """Starts the dedicated Win32 message loop thread for the overlay window."""
        self._running = True
        self._thread = threading.Thread(target=self._overlay_worker, daemon=True)
        self._thread.start()
        self._started_event.wait(timeout=2.0)

    def _overlay_worker(self):
        """Win32 window message loop running in background thread."""
        global _CLASS_REGISTERED
        try:
            import ctypes
            from ctypes import wintypes

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

            LWA_COLORKEY = 0x00000001
            LWA_ALPHA = 0x00000002

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

            hinst = kernel32.GetModuleHandleW(None)
            class_name = "DualPointerGhostOverlaySingleton"

            if not _CLASS_REGISTERED:
                wce = WNDCLASSEX()
                wce.cbSize = ctypes.sizeof(WNDCLASSEX)
                wce.style = 0x0001 | 0x0002  # CS_HREDRAW | CS_VREDRAW
                wce.lpfnWndProc = _WNDPROC_FUNC
                wce.hInstance = hinst
                wce.lpszClassName = class_name
                user32.RegisterClassExW(ctypes.byref(wce))
                _CLASS_REGISTERED = True

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
                "DualPointerGhost",
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

            user32.SetLayeredWindowAttributes(
                hwnd, COLOR_KEY, 240, LWA_COLORKEY | LWA_ALPHA
            )
            self._hwnd = hwnd
            _GLOBAL_OVERLAYS[hwnd] = self
            self._started_event.set()

            msg = wintypes.MSG()
            while self._running:
                try:
                    while True:
                        cmd, args = self._cmd_queue.get_nowait()
                        if cmd == "SHOW":
                            x, y = args
                            user32.SetWindowPos(
                                hwnd,
                                HWND_TOPMOST,
                                x,
                                y,
                                self.size,
                                self.size,
                                SWP_NOACTIVATE | SWP_SHOWWINDOW,
                            )
                            user32.InvalidateRect(hwnd, None, True)
                        elif cmd == "HIDE":
                            user32.ShowWindow(hwnd, SW_HIDE)
                        elif cmd == "STOP":
                            self._running = False
                            _GLOBAL_OVERLAYS.pop(hwnd, None)
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

    def show(self, x: int, y: int, slot_num: int = 1):
        """Displays the ghost overlay at (x, y) with the specified slot badge."""
        if not self.enabled:
            return

        self.current_pos = (x, y)
        self.current_slot = slot_num
        self.is_visible = True
        self._cmd_queue.put(("SHOW", (x, y)))

    def hide(self):
        """Hides the ghost overlay window."""
        self.is_visible = False
        self._cmd_queue.put(("HIDE", None))

    def set_enabled(self, enabled: bool):
        """Toggles whether the ghost cursor overlay is enabled."""
        self.enabled = enabled
        if not enabled and self.is_visible:
            self.hide()

    def stop(self):
        """Cleans up and destroys the overlay window."""
        self.hide()
        self._cmd_queue.put(("STOP", None))
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
