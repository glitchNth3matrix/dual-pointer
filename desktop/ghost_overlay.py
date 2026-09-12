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


class GhostOverlay:
    """Manages the visual indicator for the parked cursor."""

    def __init__(self, enabled: bool = True, size: int = 40):
        self.enabled = enabled
        self.size = size
        self.is_visible = False
        self.current_pos: Tuple[int, int] = (0, 0)
        self.current_slot: int = 1

        self._thread: Optional[threading.Thread] = None
        self._cmd_queue: queue.Queue = queue.Queue()
        self._hwnd = None
        self._running = False

        if sys.platform == "win32" and self.enabled:
            self._start_overlay_thread()

    def _start_overlay_thread(self):
        """Starts the dedicated Win32 message loop thread for the overlay window."""
        self._running = True
        self._thread = threading.Thread(target=self._overlay_worker, daemon=True)
        self._thread.start()

    def _overlay_worker(self):
        """Win32 window message loop running in background thread."""
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            kernel32 = ctypes.windll.kernel32

            WS_POPUP = 0x80000000
            WS_EX_TOPMOST = 0x00000008
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_NOACTIVATE = 0x08000000

            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            SWP_HIDEWINDOW = 0x0080
            HWND_TOPMOST = -1

            LWA_COLORKEY = 0x00000001
            LWA_ALPHA = 0x00000002

            COLOR_KEY = 0x00FF00FF  # Magenta transparent key

            WNDPROC = ctypes.WINFUNCTYPE(
                ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
            )

            def wnd_proc(hwnd, msg, wparam, lparam):
                if msg == 0x000F:  # WM_PAINT
                    class PAINTSTRUCT(ctypes.Structure):
                        _fields_ = [
                            ("hdc", wintypes.HDC),
                            ("fErase", wintypes.BOOL),
                            ("rcPaint", wintypes.RECT),
                            ("fRestore", wintypes.BOOL),
                            ("fIncUpdate", wintypes.BOOL),
                            ("rgbReserved", ctypes.c_byte * 32),
                        ]

                    ps = PAINTSTRUCT()
                    hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))

                    # Fill background with transparent color key
                    rect = wintypes.RECT(0, 0, self.size, self.size)
                    bg_brush = gdi32.CreateSolidBrush(COLOR_KEY)
                    user32.FillRect(hdc, ctypes.byref(rect), bg_brush)
                    gdi32.DeleteObject(bg_brush)

                    # Determine badge color based on slot
                    badge_color = 0x00D08000 if self.current_slot == 1 else 0x002080FF
                    badge_brush = gdi32.CreateSolidBrush(badge_color)
                    white_brush = gdi32.CreateSolidBrush(0x00FFFFFF)
                    black_pen = gdi32.CreatePen(0, 1, 0x00000000)

                    old_brush = gdi32.SelectObject(hdc, white_brush)
                    old_pen = gdi32.SelectObject(hdc, black_pen)

                    # Draw cursor pointer polygon
                    class POINT(ctypes.Structure):
                        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

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

                    # Draw slot badge circle
                    gdi32.SelectObject(hdc, badge_brush)
                    gdi32.Ellipse(hdc, 16, 16, 36, 36)

                    # Draw slot number text
                    gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
                    gdi32.SetTextColor(hdc, 0x00FFFFFF)
                    text = str(self.current_slot)
                    badge_rect = wintypes.RECT(16, 16, 36, 36)
                    user32.DrawTextW(hdc, text, len(text), ctypes.byref(badge_rect), 0x00000001 | 0x00000004 | 0x00000020)  # DT_CENTER | DT_VCENTER | DT_SINGLELINE

                    # Clean up
                    gdi32.SelectObject(hdc, old_brush)
                    gdi32.SelectObject(hdc, old_pen)
                    gdi32.DeleteObject(badge_brush)
                    gdi32.DeleteObject(white_brush)
                    gdi32.DeleteObject(black_pen)

                    user32.EndPaint(hwnd, ctypes.byref(ps))
                    return 0

                elif msg == 0x0002:  # WM_DESTROY
                    user32.PostQuitMessage(0)
                    return 0

                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

            # Register Window Class
            proc_delegate = WNDPROC(wnd_proc)
            class WNDCLASSEX(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("style", wintypes.UINT),
                    ("lpfnWndProc", WNDPROC),
                    ("cbClsExtra", ctypes.c_int),
                    ("cbWndExtra", ctypes.c_int),
                    ("hInstance", wintypes.HINSTANCE),
                    ("hIcon", wintypes.HICON),
                    ("hCursor", wintypes.HCURSOR),
                    ("hbrBackground", wintypes.HBRUSH),
                    ("lpszMenuName", wintypes.LPCWSTR),
                    ("lpszClassName", wintypes.LPCWSTR),
                    ("hIconSm", wintypes.HICON),
                ]

            hinst = kernel32.GetModuleHandleW(None)
            class_name = "DualPointerGhostOverlay"

            wce = WNDCLASSEX()
            wce.cbSize = ctypes.sizeof(WNDCLASSEX)
            wce.style = 0x0001 | 0x0002  # CS_HREDRAW | CS_VREDRAW
            wce.lpfnWndProc = proc_delegate
            wce.hInstance = hinst
            wce.lpszClassName = class_name
            user32.RegisterClassExW(ctypes.byref(wce))

            # Create Layered Window
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

            # Set layered color key for complete transparency of background
            user32.SetLayeredWindowAttributes(
                hwnd, COLOR_KEY, 235, LWA_COLORKEY | LWA_ALPHA
            )
            self._hwnd = hwnd

            # Message pump loop with non-blocking peek to process internal queue
            msg = wintypes.MSG()
            while self._running:
                # Process incoming commands from Python main thread
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
                            user32.ShowWindow(hwnd, SWP_HIDEWINDOW)
                        elif cmd == "STOP":
                            self._running = False
                            user32.DestroyWindow(hwnd)
                            break
                        self._cmd_queue.task_done()
                except queue.Empty:
                    pass

                # Windows message pump
                while user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):  # PM_REMOVE = 1
                    if msg.message == 0x0012:  # WM_QUIT
                        self._running = False
                        break
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))

                time.sleep(0.01)

        except Exception:
            # Headless or non-win32 fallback
            pass

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
