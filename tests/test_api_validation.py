import json
from unittest.mock import Mock

import pytest

from framework.api import ApiResponseValidator


@pytest.mark.parametrize(
    "status",
    [200, 201, 204, 400, 401, 404, 500],
)
def test_assert_status_accepts_matching_status(status):
    response = Mock(status=status)

    ApiResponseValidator.assert_status(response, status)


def test_assert_status_rejects_mismatched_status():
    response = Mock(status=404)

    with pytest.raises(
        AssertionError,
        match="Expected HTTP status 200, but received 404",
    ):
        ApiResponseValidator.assert_status(response, 200)


@pytest.mark.parametrize(
    "expected_status",
    [0, 99, 600, -1, True, False, 200.5, "200", None],
)
def test_assert_status_rejects_invalid_expected_status(
    expected_status,
):
    response = Mock(status=200)

    with pytest.raises(
        ValueError,
        match="expected_status must be an HTTP status code",
    ):
        ApiResponseValidator.assert_status(
            response,
            expected_status,
        )


@pytest.mark.parametrize(
    "json_data",
    [
        {"message": "success"},
        {"user": {"id": 1, "name": "Kabir"}},
        [1, 2, 3],
        "success",
        123,
        True,
        None,
    ],
)
def test_assert_json_returns_parsed_json(json_data):
    response = Mock()
    response.json.return_value = json_data

    result = ApiResponseValidator.assert_json(response)

    assert result == json_data


def test_assert_json_rejects_invalid_json():
    response = Mock()
    response.json.side_effect = json.JSONDecodeError(
        "Expecting value",
        "invalid-json",
        0,
    )

    with pytest.raises(
        AssertionError,
        match="Response body is not valid JSON",
    ):
        ApiResponseValidator.assert_json(response)


def test_assert_json_rejects_value_error():
    response = Mock()
    response.json.side_effect = ValueError(
        "Invalid response body"
    )

    with pytest.raises(
        AssertionError,
        match="Response body is not valid JSON",
    ):
        ApiResponseValidator.assert_json(response)


def test_assert_json_field_accepts_matching_value():
    response = Mock()
    response.json.return_value = {
        "status": "success",
        "count": 5,
    }

    ApiResponseValidator.assert_json_field(
        response,
        "status",
        "success",
    )


def test_assert_json_field_rejects_missing_field():
    response = Mock()
    response.json.return_value = {"status": "success"}

    with pytest.raises(
        AssertionError,
        match="Expected JSON field 'message' to exist",
    ):
        ApiResponseValidator.assert_json_field(
            response,
            "message",
            "Hello",
        )


def test_assert_json_field_rejects_wrong_value():
    response = Mock()
    response.json.return_value = {"status": "failed"}

    with pytest.raises(
        AssertionError,
        match="Expected JSON field 'status'",
    ):
        ApiResponseValidator.assert_json_field(
            response,
            "status",
            "success",
        )


def test_assert_json_field_rejects_non_object_json():
    response = Mock()
    response.json.return_value = [1, 2, 3]

    with pytest.raises(
        AssertionError,
        match="Expected JSON response to be an object",
    ):
        ApiResponseValidator.assert_json_field(
            response,
            "status",
            "success",
        )


@pytest.mark.parametrize(
    "field",
    ["", "   ", None, 123],
)
def test_assert_json_field_rejects_invalid_field_name(field):
    response = Mock()

    with pytest.raises(
        ValueError,
        match="field must be a non-empty string",
    ):
        ApiResponseValidator.assert_json_field(
            response,
            field,
            "success",
        )


@pytest.mark.parametrize(
    ("actual_name", "requested_name"),
    [
        ("Content-Type", "Content-Type"),
        ("content-type", "CONTENT-TYPE"),
        ("X-Request-ID", "x-request-id"),
    ],
)
def test_assert_header_accepts_case_insensitive_name(
    actual_name,
    requested_name,
):
    response = Mock()
    response.headers = {actual_name: "application/json"}

    ApiResponseValidator.assert_header(
        response,
        requested_name,
        "application/json",
    )


def test_assert_header_accepts_empty_value():
    response = Mock()
    response.headers = {"X-Empty": ""}

    ApiResponseValidator.assert_header(
        response,
        "X-Empty",
        "",
    )


def test_assert_header_rejects_missing_header():
    response = Mock()
    response.headers = {"Content-Type": "application/json"}

    with pytest.raises(
        AssertionError,
        match="Expected response header 'X-Request-ID' to exist",
    ):
        ApiResponseValidator.assert_header(
            response,
            "X-Request-ID",
            "123",
        )


def test_assert_header_rejects_wrong_value():
    response = Mock()
    response.headers = {"Content-Type": "text/plain"}

    with pytest.raises(
        AssertionError,
        match="Expected response header 'Content-Type'",
    ):
        ApiResponseValidator.assert_header(
            response,
            "Content-Type",
            "application/json",
        )


@pytest.mark.parametrize(
    "name",
    ["", "   ", None, 123],
)
def test_assert_header_rejects_invalid_name(name):
    response = Mock()
    response.headers = {}

    with pytest.raises(
        ValueError,
        match="header name must be a non-empty string",
    ):
        ApiResponseValidator.assert_header(
            response,
            name,
            "application/json",
        )


@pytest.mark.parametrize(
    "expected_value",
    [None, 123, True],
)
def test_assert_header_rejects_non_string_expected_value(
    expected_value,
):
    response = Mock()
    response.headers = {"Content-Type": "application/json"}

    with pytest.raises(
        ValueError,
        match="expected_value must be a string",
    ):
        ApiResponseValidator.assert_header(
            response,
            "Content-Type",
            expected_value,
        )
