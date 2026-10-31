
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
