# API Testing with PRAMAN

PRAMAN provides the `praman_api` Pytest fixture for making HTTP API requests through its `ApiClient` abstraction, powered by Playwright.

The fixture handles API configuration, request headers, authentication, and API request context lifecycle. You can use it directly in your Pytest tests without manually creating or disposing of a Playwright API request context.

## 1. Prerequisites

Before using API testing:

- Install PRAMAN in your client project's Python environment.
- Follow the client setup instructions in [README.md](README.md).
- Ensure your YAML configuration defines a valid `base_url` and `timeout` for the selected environment.
- Ensure the API endpoint is accessible from the test environment.

For JSON Schema response validation, install the optional dependency:

```powershell
pip install "praman[api-schema]"
```

This extra installs the `jsonschema` package required for Draft 2020-12 validation. It is not required for the other API client features.

## 2. Configuration

Set both required environment variables in PowerShell:

```powershell
$env:PRAMAN_CONFIG_FILE = "D:\client-project\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
```

Your YAML configuration should define the API's base URL and timeout under the selected environment.

For example:

```yaml
environments:
  development:
    base_url: "https://api.example.com"
    timeout: 30000
```

Use the configuration structure supported by your installed PRAMAN version.

## 3. Example API Test

The following example checks a health endpoint:

```python
def test_health_endpoint(praman_api):
    response = praman_api.get("/health")

    assert response.status == 200
    assert response.json() == {"status": "ok"}
```

This example assumes the configured API provides a `/health` endpoint and returns:

```json
{
    "status": "ok"
}
```

Replace the endpoint and assertions with those appropriate for an authorized test environment.

## 4. Supported HTTP Methods

The `praman_api` fixture provides the following HTTP methods:

- `get(url, **kwargs)`
- `post(url, **kwargs)`
- `put(url, **kwargs)`
- `patch(url, **kwargs)`
- `delete(url, **kwargs)`

Request options are forwarded to Playwright's API request context. This allows you to use supported Playwright request options without PRAMAN needing to reimplement the HTTP transport.

### Example: GET request

```python
def test_get_users(praman_api):
    response = praman_api.get("/users")

    assert response.status == 200
```

### Example: POST request

```python
def test_create_user(praman_api):
    response = praman_api.post(
        "/users",
        data={"name": "Test User"},
    )

    assert response.status == 201
```

The examples assume that the API supports these endpoints and expected status codes. Adapt them to your API's contract.

## 5. Working with API Responses

The returned response is the Playwright `APIResponse` object.

You can use its response properties and methods, including:

- `status` — HTTP status code.
- `ok` — whether the response indicates a successful status.
- `headers` — response headers.
- `json()` — parse a JSON response body.
- `text()` — read the response body as text.

Example:

```python
def test_user_response(praman_api):
    response = praman_api.get("/users/1")

    assert response.status == 200

    user = response.json()

    assert "id" in user
    assert "name" in user
```

The expected response structure must match the API being tested.

## 6. Response Validation

PRAMAN provides `ApiResponseValidator` for reusable API response assertions.

Import it from the public API:

```python
from framework.api import ApiResponseValidator
```

### HTTP status validation

Use `assert_status()` to check the expected HTTP status code:

```python
def test_health_status(praman_api):
    response = praman_api.get("/health")

    ApiResponseValidator.assert_status(response, 200)
```

The validator accepts HTTP status codes from 100 to 599, including error status codes for negative API tests.

### JSON response validation

Use `assert_json()` to parse and validate that the response body contains valid JSON:

```python
def test_response_contains_valid_json(praman_api):
    response = praman_api.get("/users")

    data = ApiResponseValidator.assert_json(response)

    assert isinstance(data, list)
```

The method returns the parsed JSON data. Invalid JSON raises an `AssertionError`.

### JSON field validation

Use `assert_json_field()` to check a top-level field in a JSON object:

```python
def test_user_name(praman_api):
    response = praman_api.get("/users/1")

    ApiResponseValidator.assert_json_field(
        response,
        "name",
        "Test User",
    )
```

This method validates top-level JSON object fields.

### Nested JSON path validation

Use `assert_json_path()` to validate values inside nested JSON objects and arrays.

For example, consider this API response:

```json
{
    "user": {
        "profile": {
            "email": "user@example.com",
            "age": 30
        }
    },
    "orders": [
        {
            "id": 101
        },
        {
            "id": 102
        }
    ]
}
```

To validate a nested dictionary value:

```python
def test_user_email(praman_api):
    response = praman_api.get("/users/1")

    ApiResponseValidator.assert_json_path(
        response,
        "user.profile.email",
        "user@example.com",
    )
```

To validate an item inside a JSON array:

```python
def test_second_order_id(praman_api):
    response = praman_api.get("/users/1")

    ApiResponseValidator.assert_json_path(
        response,
        "orders.1.id",
        102,
    )
```

The path uses dot-separated segments:

- Dictionary keys identify object properties.
- Numeric segments identify list indexes when the current value is a list.
- List indexes start at `0`.

The validator raises an `AssertionError` when a key or index does not exist, traversal cannot continue, or the actual value differs from the expected value.

An invalid or empty path raises a `ValueError`.

**Current limitation:** Dictionary keys containing literal dots are not supported by this simple dot-notation format.

### Response header validation

Use `assert_header()` to check that a response header exists and has the expected value:

```python
def test_response_content_type(praman_api):
    response = praman_api.get("/health")

    ApiResponseValidator.assert_header(
        response,
        "Content-Type",
        "application/json",
    )
```

Header names are matched case-insensitively. Header values are compared exactly.

### JSON Schema validation

PRAMAN supports JSON Schema Draft 2020-12 response validation through `assert_json_schema()`.

This allows you to validate the structure and data types of an API response against a reusable schema instead of writing individual assertions for every field.

**Installation**

JSON Schema validation is an optional feature. Install it with:

```powershell
pip install "praman[api-schema]"
```

You do not need this extra to use the other PRAMAN API features.

**Example response**

Assume the API returns:

```json
{
    "id": 101,
    "name": "Test User",
    "email": "user@example.com",
    "active": true
}
```

**Define a JSON Schema**

Pass the schema as a Python dictionary:

```python
USER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
        },
        "name": {
            "type": "string",
        },
        "email": {
            "type": "string",
            "format": "email",
        },
        "active": {
            "type": "boolean",
        },
    },
    "required": [
        "id",
        "name",
        "email",
        "active",
    ],
    "additionalProperties": False,
}
```

**Validate an API response**

```python
def test_user_matches_schema(praman_api):
    response = praman_api.get("/users/101")

    ApiResponseValidator.assert_status(response, 200)

    ApiResponseValidator.assert_json_schema(
        response,
        USER_SCHEMA,
    )
```

The validator:

1. Checks that the supplied schema is valid Draft 2020-12 JSON Schema.
2. Parses the API response as JSON.
3. Validates the response data against the schema.
4. Reports all detected schema validation errors, including their JSON paths.

**Validation errors**

- `ImportError`: The optional `jsonschema` dependency is not installed. Install it using `pip install "praman[api-schema]"`.
- `ValueError`: The supplied JSON Schema is invalid.
- `AssertionError`: The response contains invalid JSON or does not conform to the supplied schema.

The validator also supports JSON Schema boolean schemas (`True` and `False`).

**Important:** The schema validates the response structure and data constraints. It does not independently verify that the API's business logic or returned values are correct.

## 7. Authentication

PRAMAN supports Bearer token authentication through an environment variable.

Configure authentication in your YAML file:

```yaml
api:
  authentication:
    type: bearer
    token_env: PRAMAN_API_TOKEN
```

Set the token in PowerShell:

```powershell
$env:PRAMAN_API_TOKEN = "your-test-token"
```

PRAMAN reads the token from the environment at runtime and builds the Authorization header.

**Security recommendations:**

- Do not store real API tokens in YAML files.
- Do not commit tokens to Git.
- Use environment variables or your CI/CD platform's secret management.
- Use test credentials with only the permissions required for the tests.

If Bearer authentication is configured, PRAMAN expects the specified environment variable to contain a valid token.

## 8. Running API Tests

Run your tests with:

```powershell
python -m pytest -v
```

To run a specific API test file:

```powershell
python -m pytest tests/test_api.py -v
```

Replace `tests/test_api.py` with the actual path to your API test file.

## 9. Fixture Lifecycle

The installed PRAMAN Pytest plugin provides the `praman_api` fixture.

When a test requests this fixture, PRAMAN:

1. Loads the selected environment configuration.
2. Builds the configured request headers.
3. Resolves the configured authentication token, if Bearer authentication is enabled.
4. Creates a Playwright API request context using the configured base URL and timeout.
5. Wraps the context in PRAMAN's `ApiClient`.
6. Provides the client to the test.
7. Disposes of the underlying Playwright API request context when the fixture finishes.

You do not need to create or dispose of the underlying Playwright context manually.

## 10. Current API Client Scope

PRAMAN's `ApiClient` is a lightweight abstraction over Playwright's API request context.

It currently provides:

- GET, POST, PUT, PATCH, and DELETE requests.
- Forwarding of supported Playwright request options.
- Playwright `APIResponse` objects as the return type.
- Integration with PRAMAN's configured request headers and Bearer authentication.
- Automatic API request context cleanup through the Pytest fixture.
- Reusable HTTP status validation.
- JSON response parsing and validation.
- Top-level JSON object field validation.
- Nested JSON dictionary and array path validation.
- Response-header validation.
- Optional JSON Schema Draft 2020-12 response validation.

The response validator provides reusable assertions for API response checks. Advanced retry policies, network control, and AI-assisted API failure analysis are not included in the current implementation.