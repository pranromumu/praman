# API testing with PRAMAN

PRAMAN provides the `praman_api` Pytest fixture for making API requests through Playwright.

## Prerequisites

Install PRAMAN in your client project's Python environment and follow the client setup instructions in [README.md](README.md). Ensure your YAML configuration defines a valid `base_url` and `timeout` for the selected environment.

## Configuration

Set both environment variables in PowerShell:

```powershell
$env:PRAMAN_CONFIG_FILE = "D:\client-project\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
```

## Example API test

```python
def test_health_endpoint(praman_api):
    response = praman_api.get("/health")

    assert response.status == 200
    assert response.json() == {"status": "ok"}
```

This example assumes the configured API provides `/health` and returns `{"status": "ok"}`. Replace the endpoint and assertions with those appropriate for an authorized test environment.

## Run the test

```powershell
python -m pytest -v
```

The installed PRAMAN Pytest plugin provides the `praman_api` fixture. It creates an API request context using the configured base URL and timeout, then disposes of that context when the fixture finishes.