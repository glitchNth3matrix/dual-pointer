import os
import tempfile
import pytest
from desktop.config import DualPointerConfig

def test_default_config():
    config = DualPointerConfig()
    assert config.hotkey_modifier == "alt"
    assert config.hotkey_key == "\\"
    assert config.ghost_cursor_enabled is True
    assert config.overlay_size == 44
    assert config.mouse_side_button == "xbutton1"
    assert config.landing_ripple is True

def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = DualPointerConfig(
            hotkey_modifier="ctrl+alt",
            hotkey_key="c",
            ghost_cursor_enabled=False,
            overlay_size=48
        )
        config.save_to_file(config_path)

        loaded = DualPointerConfig.load_from_file(config_path)
        assert loaded.hotkey_modifier == "ctrl+alt"
        assert loaded.hotkey_key == "c"
        assert loaded.ghost_cursor_enabled is False
        assert loaded.overlay_size == 48

def test_load_nonexistent_config_returns_defaults():
    loaded = DualPointerConfig.load_from_file("nonexistent_path_test_123.json")
    assert loaded.hotkey_modifier == "alt"
    assert loaded.hotkey_key == "\\"
