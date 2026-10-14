import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.cli_config import parse_cli_arguments

def test_no_cli_arguments_returns_empty_dict():
    result = parse_cli_arguments([])
    assert result == {}

def test_browser_override():
    result = parse_cli_arguments(["--browser", "firefox"])
    assert result == {"browser": "firefox"}

def test_base_url_override():
    result = parse_cli_arguments(["--base-url", "https://ci.example.com"])
    assert result == {"base_url": "https://ci.example.com"}

def test_timeout_string_converted_to_int():
    result = parse_cli_arguments(["--timeout", "60000"])
    assert result == {"timeout": 60000}
    assert isinstance(result["timeout"], int)

def test_headless_true_string_converted_to_bool():
    result = parse_cli_arguments(["--headless", "true"])
    assert result == {"headless": True}
    assert isinstance(result["headless"], bool)

def test_headless_false_string_converted_to_bool():
    result = parse_cli_arguments(["--headless", "false"])
    assert result == {"headless": False}

def test_invalid_headless_raises_error():
    with pytest.raises(ValueError, match="Invalid value for --headless"):
        parse_cli_arguments(["--headless", "maybe"])

def test_invalid_timeout_raises_error():
    with pytest.raises(ValueError, match="Invalid value for --timeout"):
        parse_cli_arguments(["--timeout", "abc"])

def test_unsupported_browser_not_rejected_here():
    result = parse_cli_arguments(["--browser", "safari"])
    assert result == {"browser": "safari"}

def test_multiple_values_together():
    result = parse_cli_arguments([
        "--base-url", "https://api.example.com",
        "--browser", "webkit",
        "--headless", "true",
        "--timeout", "10000"
    ])
    assert result == {
        "base_url": "https://api.example.com",
        "browser": "webkit",
        "headless": True,
        "timeout": 10000
    }