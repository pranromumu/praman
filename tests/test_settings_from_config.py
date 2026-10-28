import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from dataclasses import FrozenInstanceError
from framework.config.settings import Settings

def test_1_complete_configuration():
    config = {
        "base_url": "https://test.example.com",
        "browser": "firefox",
        "headless": True,
        "timeout": 10000
    }
    settings = Settings.from_config(config)
    
    assert settings.BASE_URL == "https://test.example.com"
    assert settings.BROWSER == "firefox"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 10000

def test_2_browser_default():
    config = {
        "base_url": "https://test.example.com",
        "headless": True,
        "timeout": 10000
    }
    settings = Settings.from_config(config)
    assert settings.BROWSER == "chromium"

def test_3_invalid_browser():
    config = {
        "base_url": "https://test.example.com",
        "browser": "safari",
        "headless": True,
        "timeout": 10000
    }
    with pytest.raises(ValueError, match="BROWSER must be one of"):
        Settings.from_config(config)

def test_4_invalid_timeout():
    config = {
        "base_url": "https://test.example.com",
        "browser": "firefox",
        "headless": True,
        "timeout": -1
    }
    with pytest.raises(ValueError, match="TIMEOUT must be an integer greater than 0"):
        Settings.from_config(config)

def test_5_missing_required_field():
    config = {
        "browser": "firefox",
        "headless": True,
        "timeout": 10000
    }
    with pytest.raises(ValueError, match="Missing required configuration field"):
        Settings.from_config(config)

def test_6_multiple_validation_errors():
    config = {
        "base_url": "",
        "browser": "safari",
        "headless": "false",
        "timeout": -1
    }
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config(config)
        
    error_message = str(exc_info.value)
    
    assert "BASE_URL cannot be empty" in error_message
    assert "BROWSER must be one of" in error_message
    assert "HEADLESS must be a boolean" in error_message
    assert "TIMEOUT must be an integer greater than 0" in error_message

def test_7_immutability():
    config = {
        "base_url": "https://test.example.com",
        "browser": "firefox",
        "headless": True,
        "timeout": 10000
    }
    settings = Settings.from_config(config)
    
    with pytest.raises(FrozenInstanceError):
        settings.BROWSER = "webkit"

def test_missing_required_field_stops_before_value_validation():
    config = {
        "browser": "safari",
    }
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config(config)

    error_message = str(exc_info.value)

    assert "Missing required configuration field(s)" in error_message
    assert "base_url" in error_message
    assert "headless" in error_message
    assert "timeout" in error_message
    assert "BROWSER must be one of" not in error_message

def test_settings_are_independent_of_input_config_mutations():
    config = {
        "base_url": "https://test.example.com",
        "browser": "firefox",
        "headless": True,
        "timeout": 10000,
    }

    settings = Settings.from_config(config)

    config["base_url"] = "https://changed.example.com"
    config["browser"] = "webkit"
    config["headless"] = False
    config["timeout"] = 5000

    assert settings.BASE_URL == "https://test.example.com"
    assert settings.BROWSER == "firefox"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 10000