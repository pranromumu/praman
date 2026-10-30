# API Testing with PRAMAN

PRAMAN provides the `praman_api` Pytest fixture for making HTTP API requests through its `ApiClient` abstraction, powered by Playwright.

The fixture handles API configuration, request headers, authentication, and API request context lifecycle. You can use it directly in your Pytest tests without manually creating or disposing of a Playwright API request context.

## 1. Prerequisites

Before using API testing:

- Install PRAMAN in your client project's Python environment.
- Follow the client setup instructions in [README.md](README.md).
- Ensure your YAML configuration defines a valid `base_url` and `timeout` for the selected environment.
- Ensure the API endpoint is accessible from the test environment.

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

## 6. Authentication

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

## 7. Running API Tests

Run your tests with:

```powershell
python -m pytest -v
```

To run a specific API test file:

```powershell
python -m pytest tests/test_api.py -v
```

Replace `tests/test_api.py` with the actual path to your API test file.

## 8. Fixture Lifecycle

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

## 9. Current API Client Scope

PRAMAN's `ApiClient` is a lightweight abstraction over Playwright's API request context.

It currently provides:

- GET, POST, PUT, PATCH, and DELETE requests.
- Forwarding of supported Playwright request options.
- Playwright `APIResponse` objects as the return type.
- Integration with PRAMAN's configured request headers and Bearer authentication.
- Automatic API request context cleanup through the Pytest fixture.

Advanced response validation, retry policies, and AI-assisted API failure analysis are separate development areas and should not be considered part of the current `ApiClient` functionality unless implemented and verified in a later release.