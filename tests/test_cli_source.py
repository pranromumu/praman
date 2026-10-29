import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.cli_source import CLISource
from framework.contracts.config_source import ConfigSource

def test_no_arguments_returns_empty_dict():
    source = CLISource(args=[])
    result = source.get_config()
    assert result == {}

def test_reads_browser():
    source = CLISource(args=["--browser", "firefox"])
    result = source.get_config()
    assert result == {"browser": "firefox"}

def test_reads_base_url():
    source = CLISource(args=["--base-url", "https://ci.example.com"])
    result = source.get_config()
    assert result == {"base_url": "https://ci.example.com"}

def test_converts_timeout_to_integer():
    source = CLISource(args=["--timeout", "60000"])
    result = source.get_config()
    assert result["timeout"] == 60000
    assert isinstance(result["timeout"], int)

def test_converts_headless_true():
    source = CLISource(args=["--headless", "true"])
    result = source.get_config()
    assert result["headless"] is True
    assert isinstance(result["headless"], bool)

def test_converts_headless_false():
    source = CLISource(args=["--headless", "false"])
    result = source.get_config()
    assert result["headless"] is False

def test_invalid_headless_raises_error():
    source = CLISource(args=["--headless", "maybe"])
    with pytest.raises(ValueError, match="Invalid value for --headless"):
        source.get_config()

def test_invalid_timeout_raises_error():
    source = CLISource(args=["--timeout", "abc"])
    with pytest.raises(ValueError, match="Invalid value for --timeout"):
        source.get_config()

def test_unsupported_browser_passes_through():
    # Parser does not validate business rules
    source = CLISource(args=["--browser", "safari"])
    result = source.get_config()
    assert result == {"browser": "safari"}

def test_multiple_values_together():
    source = CLISource(args=[
        "--base-url", "https://api.example.com",
        "--browser", "webkit",
        "--headless", "true",
        "--timeout", "10000"
    ])
    result = source.get_config()
    assert result == {
        "base_url": "https://api.example.com",
        "browser": "webkit",
        "headless": True,
        "timeout": 10000
    }

def test_cli_source_implements_config_source():
    source = CLISource(args=[])
    assert isinstance(source, ConfigSource)

def test_default_args_reads_sys_argv(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["praman", "--browser", "firefox"],
    )

    source = CLISource()
    result = source.get_config()

    assert result == {"browser": "firefox"}
