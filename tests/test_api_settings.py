from dataclasses import FrozenInstanceError

import pytest

from framework.config.api_settings import ApiSettings


def test_api_settings_defaults_to_empty_headers():
    settings = ApiSettings.from_config()

    assert dict(settings.HEADERS) == {}


def test_api_settings_accepts_valid_headers():
    settings = ApiSettings.from_config(
        {
            "headers": {
                "Accept": "application/json",
                "X-Client": "praman",
            }
        }
    )

    assert dict(settings.HEADERS) == {
        "Accept": "application/json",
        "X-Client": "praman",
    }


def test_api_settings_rejects_non_dictionary_configuration():
    with pytest.raises(
        ValueError,
        match="API configuration must be a dictionary",
    ):
        ApiSettings.from_config("invalid")


def test_api_settings_rejects_unknown_fields():
    with pytest.raises(
        ValueError,
        match="Unexpected API configuration field",
    ):
        ApiSettings.from_config({"token": "secret"})


@pytest.mark.parametrize(
    "headers",
    [
        None,
        "invalid",
        ["Accept", "application/json"],
        123,
    ],
)
def test_api_settings_rejects_invalid_headers_container(headers):
    with pytest.raises(
        ValueError,
        match="API headers must be a dictionary",
    ):
        ApiSettings.from_config({"headers": headers})


@pytest.mark.parametrize(
    "headers",
    [
        {"": "value"},
        {"   ": "value"},
        {123: "value"},
    ],
)
def test_api_settings_rejects_invalid_header_names(headers):
    with pytest.raises(
        ValueError,
        match="API header names must be non-empty strings",
    ):
        ApiSettings.from_config({"headers": headers})


def test_api_settings_rejects_non_string_header_values():
    with pytest.raises(
        ValueError,
        match="must have a string value",
    ):
        ApiSettings.from_config(
            {"headers": {"Accept": 123}}
        )


@pytest.mark.parametrize("value", ["hello\rworld", "hello\nworld"])
def test_api_settings_rejects_newlines_in_header_values(value):
    with pytest.raises(
        ValueError,
        match="cannot contain newline characters",
    ):
        ApiSettings.from_config(
            {"headers": {"X-Test": value}}
        )


def test_api_settings_rejects_case_insensitive_duplicate_headers():
    with pytest.raises(
        ValueError,
        match="Duplicate API header name",
    ):
        ApiSettings.from_config(
            {
                "headers": {
                    "Accept": "application/json",
                    "accept": "text/plain",
                }
            }
        )


def test_api_settings_headers_are_immutable():
    settings = ApiSettings.from_config(
        {"headers": {"Accept": "application/json"}}
    )

    with pytest.raises(TypeError):
        settings.HEADERS["Accept"] = "text/plain"


def test_api_settings_field_cannot_be_reassigned():
    settings = ApiSettings.from_config()

    with pytest.raises(FrozenInstanceError):
        settings.HEADERS = {"Accept": "application/json"}


def test_api_settings_direct_construction_is_immutable():
    original_headers = {
        "Accept": "application/json",
    }

    settings = ApiSettings(HEADERS=original_headers)

    # Mutating the original dictionary must not affect settings.
    original_headers["Accept"] = "text/plain"

    assert settings.HEADERS["Accept"] == "application/json"

    # Mutating the settings headers must also fail.
    with pytest.raises(TypeError):
        settings.HEADERS["Accept"] = "text/html"


def test_api_settings_direct_construction_rejects_invalid_headers():
    with pytest.raises(
        ValueError,
        match="must have a string value",
    ):
        ApiSettings(HEADERS={"Accept": 123})
