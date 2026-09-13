import sys
import pytest
from desktop.autostart import is_autostart_enabled, set_autostart

def test_autostart_toggle():
    if sys.platform != "win32":
        pytest.skip("Windows only")

    # Read current state
    initial_state = is_autostart_enabled()

    # Toggle to enabled
    assert set_autostart(True) is True
    assert is_autostart_enabled() is True

    # Toggle to disabled
    assert set_autostart(False) is True
    assert is_autostart_enabled() is False

    # Restore initial state
    set_autostart(initial_state)
