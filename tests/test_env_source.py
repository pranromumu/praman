import pytest

from framework.config.env_source import EnvSource
from framework.contracts.config_source import ConfigSource


def test_env_source_with_no_variables_returns_empty_dict():
    source = EnvSource(environ={})

    result = source.get_config()

    assert result == {}


def test_env_source_reads_base_url():
    source = EnvSource(
        environ={
            "PRAMAN_BASE_URL": "https://client.example.com"
        }
    )

    result = source.get_config()

    assert result["base_url"] == "https://client.example.com"


def test_env_source_reads_browser():
    source = EnvSource(
        environ={
            "PRAMAN_BROWSER": "firefox"
        }
    )

    result = source.get_config()

    assert result["browser"] == "firefox"


def test_env_source_converts_headless_true():
    source = EnvSource(
        environ={
            "PRAMAN_HEADLESS": "true"
        }
    )

    result = source.get_config()

    assert result["headless"] is True


def test_env_source_converts_headless_false():
    source = EnvSource(
        environ={
            "PRAMAN_HEADLESS": "false"
        }
    )

    result = source.get_config()

    assert result["headless"] is False


def test_env_source_headless_is_case_insensitive():
    source = EnvSource(
        environ={
            "PRAMAN_HEADLESS": "FALSE"
        }
    )

    result = source.get_config()

    assert result["headless"] is False


def test_env_source_invalid_headless_raises_error():
    source = EnvSource(
        environ={
            "PRAMAN_HEADLESS": "maybe"
        }
    )

    with pytest.raises(ValueError) as exc_info:
        source.get_config()

    assert "Invalid value for PRAMAN_HEADLESS" in str(exc_info.value)


def test_env_source_converts_timeout_to_integer():
    source = EnvSource(
        environ={
            "PRAMAN_TIMEOUT": "60000"
        }
    )

    result = source.get_config()

    assert result["timeout"] == 60000
    assert isinstance(result["timeout"], int)


def test_env_source_invalid_timeout_raises_error():
    source = EnvSource(
        environ={
            "PRAMAN_TIMEOUT": "abc"
        }
    )

    with pytest.raises(ValueError) as exc_info:
        source.get_config()

    assert "Invalid value for PRAMAN_TIMEOUT" in str(exc_info.value)


def test_env_source_does_not_validate_browser():
    source = EnvSource(
        environ={
            "PRAMAN_BROWSER": "safari"
        }
    )

    result = source.get_config()

    assert result["browser"] == "safari"


def test_env_source_returns_multiple_values():
    source = EnvSource(
        environ={
            "PRAMAN_BASE_URL": "https://client.example.com",
            "PRAMAN_BROWSER": "webkit",
            "PRAMAN_HEADLESS": "false",
            "PRAMAN_TIMEOUT": "60000",
        }
    )

    result = source.get_config()

    assert result == {
        "base_url": "https://client.example.com",
        "browser": "webkit",
        "headless": False,
        "timeout": 60000,
    }


def test_env_source_implements_config_source():
    source = EnvSource(environ={})

    assert isinstance(source, ConfigSource)