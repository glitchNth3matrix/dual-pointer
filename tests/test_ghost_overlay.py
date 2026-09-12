import pytest
from desktop.ghost_overlay import GhostOverlay

def test_ghost_overlay_initialization():
    overlay = GhostOverlay(enabled=False)
    assert not overlay.is_visible
    assert overlay.current_slot == 1
    assert overlay.current_pos == (0, 0)

def test_ghost_overlay_show_and_hide():
    overlay = GhostOverlay(enabled=True)
    try:
        overlay.show(150, 250, slot_num=2)
        assert overlay.is_visible
        assert overlay.current_pos == (150, 250)
        assert overlay.current_slot == 2

        overlay.hide()
        assert not overlay.is_visible
    finally:
        overlay.stop()

def test_ghost_overlay_disabled():
    overlay = GhostOverlay(enabled=False)
    overlay.show(100, 100, slot_num=1)
    assert not overlay.is_visible
