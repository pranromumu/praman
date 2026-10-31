from typing import Any

from playwright.sync_api import APIResponse


class ApiResponseValidator:
    """Reusable validation helpers for API responses."""

    @staticmethod
    def assert_status(
        response: APIResponse,
        expected_status: int,
    ) -> None:
        """Assert that an API response has the expected HTTP status."""

        if (
            isinstance(expected_status, bool)
            or not isinstance(expected_status, int)
            or not 100 <= expected_status <= 599
        ):
            raise ValueError(
                "expected_status must be an HTTP status code "
                "between 100 and 599"
            )

        if response.status != expected_status:
            raise AssertionError(
                f"Expected HTTP status {expected_status}, "
                f"but received {response.status}."
            )

    @staticmethod
    def assert_json(response: APIResponse) -> Any:
        """Assert that the response body contains valid JSON."""

        try:
            return response.json()
        except ValueError as exc:
            raise AssertionError(
                "Response body is not valid JSON."
            ) from exc

    @staticmethod
    def assert_json_field(
        response: APIResponse,
        field: str,
        expected_value: Any,
    ) -> None:
        """Assert that a top-level JSON field has the expected value."""

        if not isinstance(field, str) or not field.strip():
            raise ValueError("field must be a non-empty string")

        data = ApiResponseValidator.assert_json(response)

        if not isinstance(data, dict):
            raise AssertionError(
                "Expected JSON response to be an object."
            )

        if field not in data:
            raise AssertionError(
                f"Expected JSON field '{field}' to exist."
            )

        actual_value = data[field]

        if actual_value != expected_value:
            raise AssertionError(
                f"Expected JSON field '{field}' to be "
                f"{expected_value!r}, but received {actual_value!r}."
            )

    @staticmethod
    def assert_header(
        response: APIResponse,
        name: str,
        expected_value: str,
    ) -> None:
        """Assert that a response header exists and has the expected value."""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("header name must be a non-empty string")

        if not isinstance(expected_value, str):
            raise ValueError("expected_value must be a string")

        headers = response.headers

        matching_name = next(
            (
                header_name
                for header_name in headers
                if header_name.lower() == name.lower()
            ),
            None,
        )

        if matching_name is None:
            raise AssertionError(
                f"Expected response header '{name}' to exist."
            )

        actual_value = headers[matching_name]

        if actual_value != expected_value:
            raise AssertionError(
                f"Expected response header '{name}' to be "
                f"{expected_value!r}, but received {actual_value!r}."
            )

    @staticmethod
    def assert_json_path(
        response: APIResponse,
        path: str,
        expected_value: Any,
    ) -> None:
        """Assert that a nested JSON value matches the expected value.

        Supports dot-separated dictionary keys and list indexes.

        Examples:
            user.profile.email
            orders.0.id
        """

        if not isinstance(path, str) or not path.strip():
            raise ValueError("path must be a non-empty string")

        path_parts = path.split(".")

        if any(not part for part in path_parts):
            raise ValueError(
                "path must not contain empty segments"
            )

        actual_value = ApiResponseValidator.assert_json(response)
        traversed_path = []

        for part in path_parts:
            traversed_path.append(part)
            current_path = ".".join(traversed_path)

            if isinstance(actual_value, dict):
                if part not in actual_value:
                    raise AssertionError(
                        f"JSON path '{current_path}' does not exist."
                    )

                actual_value = actual_value[part]

            elif isinstance(actual_value, list):
                if not part.isdigit():
                    raise AssertionError(
                        f"Expected a numeric list index at "
                        f"JSON path '{current_path}'."
                    )

                index = int(part)

                if index >= len(actual_value):
                    raise AssertionError(
                        f"List index {index} is out of range at "
                        f"JSON path '{current_path}'."
                    )

                actual_value = actual_value[index]

            else:
                raise AssertionError(
                    f"Cannot continue JSON path '{current_path}': "
                    "the current value is not an object or array."
                )

        if actual_value != expected_value:
            raise AssertionError(
                f"Expected JSON path '{path}' to be "
                f"{expected_value!r}, but received {actual_value!r}."
            )

    @staticmethod
    def assert_json_schema(
        response: APIResponse,
        schema: dict[str, Any] | bool,
    ) -> None:
        """Assert that the response JSON conforms to a JSON Schema.

        Supports JSON Schema Draft 2020-12.

        Raises:
            ImportError: If the optional jsonschema dependency is missing.
            ValueError: If the supplied schema is invalid.
            AssertionError: If the response JSON does not match the schema.
        """

        try:
            from jsonschema import Draft202012Validator
            from jsonschema.exceptions import SchemaError
        except ModuleNotFoundError as exc:
            if exc.name == "jsonschema":
                raise ImportError(
                    "JSON Schema validation requires the optional "
                    "dependency. Install it with: "
                    'pip install "praman[api-schema]"'
                ) from exc
            raise

        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise ValueError(
                f"Invalid JSON Schema: {exc.message}"
            ) from exc

        data = ApiResponseValidator.assert_json(response)

        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )

        if errors:
            error_messages = []

            for error in errors:
                error_path = "$"

                for part in error.absolute_path:
                    if isinstance(part, int):
                        error_path += f"[{part}]"
                    else:
                        error_path += f"[{part!r}]"

                error_messages.append(
                    f"At {error_path}: {error.message}"
                )

            details = "\n".join(
                f"- {message}"
                for message in error_messages
            )

            raise AssertionError(
                "API response does not match the JSON Schema:\n"
                f"{details}"
            )
