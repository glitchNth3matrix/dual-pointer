import pytest
from desktop.ripple_overlay import LandingRippleOverlay

def test_ripple_overlay_initialization_disabled():
    overlay = LandingRippleOverlay(enabled=False)
    assert not overlay.enabled
    assert not overlay._running
    overlay.pulse(100, 200, slot_num=1)
    overlay.stop()

def test_ripple_overlay_pulse():
    overlay = LandingRippleOverlay(enabled=True)
    try:
        assert overlay.enabled
        overlay.pulse(300, 400, slot_num=2)
    finally:
        overlay.stop()
