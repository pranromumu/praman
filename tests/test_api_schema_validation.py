
from unittest.mock import Mock

import pytest

from framework.api import ApiResponseValidator


def test_assert_json_schema_accepts_valid_response():
    response = Mock()
    response.json.return_value = {
        "id": 101,
        "name": "Keyboard",
        "price": 49.99,
        "available": True,
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "price": {"type": "number"},
            "available": {"type": "boolean"},
        },
        "required": ["id", "name", "price", "available"],
        "additionalProperties": False,
    }

    ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_rejects_missing_required_property():
    response = Mock()
    response.json.return_value = {
        "id": 101,
        "name": "Keyboard",
    }

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "price": {"type": "number"},
        },
        "required": ["id", "name", "price"],
    }

    with pytest.raises(
        AssertionError,
        match="API response does not match the JSON Schema",
    ):
        ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_rejects_wrong_data_type():
    response = Mock()
    response.json.return_value = {
        "id": "101",
    }

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
    }

    with pytest.raises(
        AssertionError,
        match="is not of type 'integer'",
    ):
        ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_rejects_unexpected_property():
    response = Mock()
    response.json.return_value = {
        "id": 101,
        "admin": True,
    }

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
        "additionalProperties": False,
    }

    with pytest.raises(
        AssertionError,
        match="Additional properties are not allowed",
    ):
        ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_validates_nested_objects():
    response = Mock()
    response.json.return_value = {
        "user": {
            "profile": {
                "email": "user@example.com",
            }
        }
    }

    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string"},
                        },
                        "required": ["email"],
                    }
                },
                "required": ["profile"],
            }
        },
        "required": ["user"],
    }

    ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_validates_array_items():
    response = Mock()
    response.json.return_value = {
        "products": [
            {"id": 1, "name": "Mouse"},
            {"id": 2, "name": "Keyboard"},
        ]
    }

    schema = {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                    "required": ["id", "name"],
                },
            }
        },
        "required": ["products"],
    }

    ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_rejects_invalid_array_item():
    response = Mock()
    response.json.return_value = {
        "products": [
            {"id": 1, "name": "Mouse"},
            {"id": "invalid", "name": "Keyboard"},
        ]
    }

    schema = {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                    "required": ["id", "name"],
                },
            }
        },
    }

    with pytest.raises(
        AssertionError,
        match="is not of type 'integer'",
    ):
        ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_accepts_nullable_property():
    response = Mock()
    response.json.return_value = {
        "name": "Keyboard",
        "description": None,
    }

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {
                "type": ["string", "null"],
            },
        },
        "required": ["name", "description"],
    }

    ApiResponseValidator.assert_json_schema(response, schema)


def test_assert_json_schema_reports_multiple_errors():
    response = Mock()
    response.json.return_value = {
        "id": "invalid",
        "name": 123,
    }

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        "required": ["id", "name"],
    }

    with pytest.raises(AssertionError) as exc_info:
        ApiResponseValidator.assert_json_schema(response, schema)

    message = str(exc_info.value)

    assert "['id']" in message
    assert "['name']" in message
    assert message.count("At $") == 2


def test_assert_json_schema_rejects_invalid_schema():
    response = Mock()
    response.json.return_value = {"id": 101}

    invalid_schema = {
        "type": "not-a-valid-json-schema-type",
    }

    with pytest.raises(
        ValueError,
        match="Invalid JSON Schema",
    ):
        ApiResponseValidator.assert_json_schema(
            response,
            invalid_schema,
        )


def test_assert_json_schema_rejects_invalid_response_json():
    response = Mock()
    response.json.side_effect = ValueError("Invalid JSON")

    schema = {
        "type": "object",
    }

    with pytest.raises(
        AssertionError,
        match="Response body is not valid JSON",
    ):
        ApiResponseValidator.assert_json_schema(response, schema)


@pytest.mark.parametrize(
    ("schema", "response_data"),
    [
        (True, {"anything": "allowed"}),
        (False, {"anything": "rejected"}),
    ],
)
def test_assert_json_schema_supports_boolean_schemas(
    schema,
    response_data,
):
    response = Mock()
    response.json.return_value = response_data

    if schema is True:
        ApiResponseValidator.assert_json_schema(response, schema)
    else:
        with pytest.raises(AssertionError):
            ApiResponseValidator.assert_json_schema(response, schema)
