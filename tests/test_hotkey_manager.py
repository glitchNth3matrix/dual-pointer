import pytest
from desktop.hotkey_manager import parse_hotkey_string

def test_parse_hotkey_string_alt_backslash():
    mod, vk = parse_hotkey_string("alt", "\\")
    assert mod & 0x0001  # MOD_ALT
    assert vk == 0xDC    # VK_OEM_5

def test_parse_hotkey_string_ctrl_alt():
    mod, vk = parse_hotkey_string("ctrl+alt", "c")
    assert mod & 0x0001  # MOD_ALT
    assert mod & 0x0002  # MOD_CONTROL
    assert vk == 0x43    # 'C'

def test_parse_hotkey_string_f8():
    mod, vk = parse_hotkey_string("none", "f8")
    assert vk == 0x77    # VK_F8
