
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from framework.config.env_config import parse_environment_variables


def test_no_environment_variables_returns_empty_dict(monkeypatch):
    """Return an empty dictionary when no PRAMAN environment variables are set."""
    monkeypatch.delenv("PRAMAN_BASE_URL", raising=False)
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    monkeypatch.delenv("PRAMAN_HEADLESS", raising=False)
    monkeypatch.delenv("PRAMAN_TIMEOUT", raising=False)

    result = parse_environment_variables()

    assert result == {}


def test_browser_override(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")

    result = parse_environment_variables()

    assert result == {"browser": "firefox"}


def test_base_url_override(monkeypatch):
    monkeypatch.setenv("PRAMAN_BASE_URL", "https://ci.example.com")

    result = parse_environment_variables()

    assert result == {"base_url": "https://ci.example.com"}


def test_timeout_string_converted_to_int(monkeypatch):
    monkeypatch.setenv("PRAMAN_TIMEOUT", "60000")

    result = parse_environment_variables()

    assert result == {"timeout": 60000}
    assert isinstance(result["timeout"], int)


@pytest.mark.parametrize(
    ("timeout_value", "expected"),
    [
        (" 30 ", 30),
        ("\t45\n", 45),
    ],
)
def test_timeout_parsing_accepts_surrounding_whitespace(
    monkeypatch,
    timeout_value,
    expected,
):
    monkeypatch.setenv("PRAMAN_TIMEOUT", timeout_value)

    result = parse_environment_variables()

    assert result == {"timeout": expected}
    assert isinstance(result["timeout"], int)


def test_headless_true_string_converted_to_bool(monkeypatch):
    monkeypatch.setenv("PRAMAN_HEADLESS", "true")

    result = parse_environment_variables()

    assert result == {"headless": True}
    assert isinstance(result["headless"], bool)


def test_headless_false_string_converted_to_bool(monkeypatch):
    monkeypatch.setenv("PRAMAN_HEADLESS", "false")

    result = parse_environment_variables()

    assert result == {"headless": False}
    assert isinstance(result["headless"], bool)


@pytest.mark.parametrize(
    ("headless_value", "expected"),
    [
        ("TRUE", True),
        ("FALSE", False),
        ("TrUe", True),
    ],
)
def test_headless_parsing_is_case_insensitive(
    monkeypatch,
    headless_value,
    expected,
):
    monkeypatch.setenv("PRAMAN_HEADLESS", headless_value)

    result = parse_environment_variables()

    assert result == {"headless": expected}


@pytest.mark.parametrize(
    ("headless_value", "expected"),
    [
        (" true ", True),
        (" false ", False),
        ("\tTRUE\n", True),
    ],
)
def test_headless_parsing_trims_surrounding_whitespace(
    monkeypatch,
    headless_value,
    expected,
):
    monkeypatch.setenv("PRAMAN_HEADLESS", headless_value)

    result = parse_environment_variables()

    assert result == {"headless": expected}


@pytest.mark.parametrize(
    "headless_value",
    [
        "yes",
        "   ",
        "\t\n",
    ],
)
def test_invalid_headless_raises_error(monkeypatch, headless_value):
    monkeypatch.setenv("PRAMAN_HEADLESS", headless_value)

    with pytest.raises(
        ValueError,
        match="Invalid value for PRAMAN_HEADLESS",
    ):
        parse_environment_variables()


@pytest.mark.parametrize(
    "timeout_value",
    [
        "abc",
        "30.5",
        "1e3",
    ],
)
def test_invalid_timeout_raises_error(monkeypatch, timeout_value):
    monkeypatch.setenv("PRAMAN_TIMEOUT", timeout_value)

    with pytest.raises(
        ValueError,
        match="Invalid value for PRAMAN_TIMEOUT",
    ):
        parse_environment_variables()


@pytest.mark.parametrize(
    "timeout_value",
    [
        "   ",
        "\t\n",
    ],
)
def test_whitespace_only_timeout_raises_error(
    monkeypatch,
    timeout_value,
):
    monkeypatch.setenv("PRAMAN_TIMEOUT", timeout_value)

    with pytest.raises(
        ValueError,
        match="Invalid value for PRAMAN_TIMEOUT",
    ):
        parse_environment_variables()


@pytest.mark.parametrize(
    "timeout_value",
    [
        "0",
        "-1",
        "-100",
    ],
)
def test_non_positive_timeout_raises_error(
    monkeypatch,
    timeout_value,
):
    monkeypatch.setenv("PRAMAN_TIMEOUT", timeout_value)

    with pytest.raises(
        ValueError,
        match="Invalid value for PRAMAN_TIMEOUT",
    ):
        parse_environment_variables()



def test_unsupported_browser_not_rejected_here(monkeypatch):
    """Parsing environment variables does not validate browser business rules."""
    monkeypatch.setenv("PRAMAN_BROWSER", "safari")

    result = parse_environment_variables()

    assert result == {"browser": "safari"}
