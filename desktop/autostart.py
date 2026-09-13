"""
Windows Registry Autostart Manager for DualPointer.
Manages launch-on-boot configuration in HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.
"""

import sys
import os

REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "DualPointer"


def is_autostart_enabled() -> bool:
    """Checks whether DualPointer is configured to launch on Windows startup."""
    if sys.platform != "win32":
        return False

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_READ) as key:
            try:
                val, _ = winreg.QueryValueEx(key, APP_NAME)
                return bool(val)
            except FileNotFoundError:
                return False
    except Exception:
        return False


def set_autostart(enabled: bool) -> bool:
    """Enables or disables DualPointer launching on Windows startup."""
    if sys.platform != "win32":
        return False

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_WRITE) as key:
            if enabled:
                # Use pythonw.exe if available to run silently without a console window
                python_exe = sys.executable
                pythonw = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
                exe = pythonw if os.path.exists(pythonw) else python_exe

                script_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "dual_pointer.py")
                )
                cmd = f'"{exe}" "{script_path}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"Error setting autostart registry key: {e}")
        return False
