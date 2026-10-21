
import pytest

from framework.config.environment import Environment


def test_from_string_returns_staging_environment():
    result = Environment.from_string("staging")

    assert result is Environment.STAGING

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

def test_from_string_rejects_empty_environment_name():
    with pytest.raises(
        ValueError,
        match="Environment name must not be empty",
    ):
        Environment.from_string("")