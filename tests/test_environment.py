
import pytest

from framework.config.environment import Environment


@pytest.mark.parametrize(
    ("environment", "expected_value"),
    [
        (Environment.DEVELOPMENT, "development"),
        (Environment.STAGING, "staging"),
        (Environment.PRODUCTION, "production"),
    ],
)
def test_environment_enum_values_are_stable(environment, expected_value):
    assert environment.value == expected_value

@pytest.mark.parametrize(
    ("env_name", "expected"),
    [
        ("development", Environment.DEVELOPMENT),
        ("staging", Environment.STAGING),
        ("production", Environment.PRODUCTION),
    ],
)
def test_from_string_returns_correct_environment(env_name, expected):
    result = Environment.from_string(env_name)

    assert result is expected


@pytest.mark.parametrize(
    "env_name",
    [
        "STAGING",
        " Staging ",
        "  STAGING  ",
    ],
)
def test_from_string_normalizes_environment_name(env_name):
    result = Environment.from_string(env_name)

    assert result is Environment.STAGING


def test_from_string_rejects_unsupported_environment():
    with pytest.raises(
        ValueError,
        match="Unsupported environment",
    ):
        Environment.from_string("testing")


@pytest.mark.parametrize(
    "invalid_name",
    [
        None,
        123,
        True,
        [],
    ],
)
def test_from_string_rejects_non_string_input(invalid_name):
    with pytest.raises(
        ValueError,
        match="Environment name must be a string",
    ):
        Environment.from_string(invalid_name)


@pytest.mark.parametrize(
    "env_name",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_from_string_rejects_empty_environment_name(env_name):
    with pytest.raises(
        ValueError,
        match="Environment name must not be empty",
    ):
        Environment.from_string(env_name)
