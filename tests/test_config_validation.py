import pytest

from framework.config.config_validation import validate_config


def test_validate_config_returns_dictionary_unchanged():
    config = {
        "browser": "chromium",
        "timeout": 5000,
    }

    result = validate_config(config, "TestSource")

    assert result is config
    assert result == config


@pytest.mark.parametrize(
    "invalid_config",
    [
        None,
        [],
        "invalid",
        123,
    ],
)
def test_validate_config_rejects_non_dictionary(invalid_config):
    with pytest.raises(TypeError):
        validate_config(invalid_config, "TestSource")


def test_validate_config_error_identifies_source_and_actual_type():
    with pytest.raises(
        TypeError,
        match=r"Configuration source TestSource must return a dict, got NoneType",
    ):
        validate_config(None, "TestSource")