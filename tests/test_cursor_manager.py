import pytest
from desktop.cursor_manager import CursorManager, ScreenBounds

def test_cursor_slots_initialization():
    manager = CursorManager(initial_pos_1=(100, 100), initial_pos_2=(500, 500))
    assert manager.active_slot == 1
    assert manager.slot_1 == (100, 100)
    assert manager.slot_2 == (500, 500)
    assert manager.inactive_slot == 2
    assert manager.inactive_slot_pos == (500, 500)

def test_switch_slot():
    manager = CursorManager(initial_pos_1=(100, 100), initial_pos_2=(500, 500))
    # Switch from slot 1 to slot 2, recording current pos as (120, 130)
    target_pos = manager.switch_slot(current_pos=(120, 130))
    assert manager.active_slot == 2
    assert manager.slot_1 == (120, 130)
    assert manager.slot_2 == (500, 500)
    assert target_pos == (500, 500)
    assert manager.inactive_slot == 1
    assert manager.inactive_slot_pos == (120, 130)

    # Switch back from slot 2 to slot 1, recording current pos as (550, 560)
    target_pos_2 = manager.switch_slot(current_pos=(550, 560))
    assert manager.active_slot == 1
    assert manager.slot_1 == (120, 130)
    assert manager.slot_2 == (550, 560)
    assert target_pos_2 == (120, 130)

def test_coordinate_clamping():
    bounds = ScreenBounds(left=0, top=0, width=1920, height=1080)
    manager = CursorManager(screen_bounds_provider=lambda: bounds)

    # Within bounds
    assert manager.clamp_coordinates((500, 500)) == (500, 500)
    # Outside left/top
    assert manager.clamp_coordinates((-50, -20)) == (0, 0)
    # Outside right/bottom
    assert manager.clamp_coordinates((2500, 1200)) == (1919, 1079)

def test_multi_monitor_negative_bounds():
    # Primary at 0,0 (1920x1080), Secondary monitor to the left at -1920,0 (1920x1080)
    bounds = ScreenBounds(left=-1920, top=0, width=3840, height=1080)
    manager = CursorManager(screen_bounds_provider=lambda: bounds)

    assert manager.clamp_coordinates((-1000, 500)) == (-1000, 500)
    assert manager.clamp_coordinates((-2500, 500)) == (-1920, 500)
    assert manager.clamp_coordinates((2000, 500)) == (1919, 500)
