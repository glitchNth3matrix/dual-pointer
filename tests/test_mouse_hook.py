import pytest
from desktop.mouse_hook import MouseHookManager

def test_mouse_hook_initialization():
    manager = MouseHookManager(on_trigger=lambda: None)
    assert not manager.is_running
    assert manager.target_button == "xbutton1"

def test_mouse_hook_disabled():
    triggered = []
    manager = MouseHookManager(on_trigger=lambda: triggered.append(1))
    manager.start(target_button="none")
    assert not manager.is_running
    manager.stop()
