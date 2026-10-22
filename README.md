# Praman

**A modular Python QA automation framework built around configuration management, browser automation, and extensible integration contracts.**

Praman provides a foundation for managing test configuration and running browser-based tests with Pytest and Playwright.

> **Development status:** Praman is under active development. The local test suite currently passes, but public CI execution, packaging, and release readiness still need to be verified.

## Current capabilities

- **Browser sessions:** A context-managed Playwright browser-page helper.
- **Pytest integration:** A `praman_page` fixture that loads explicit configuration and provides a browser page to tests.
- **Environment configuration:** YAML configuration organized by environment.
- **Configuration overrides:** YAML, environment-variable, and command-line configuration sources.
- **Validation:** Checks for required configuration fields, supported browser names, positive timeouts, and version-policy values.
- **Extensible configuration architecture:** Source contracts, dependency injection, version negotiation, normalization, and registry-related components.
- **Automated tests:** Tests covering browser sessions, configuration, compatibility, contracts, and related framework behavior.
- **GitHub Actions workflow:** A CI workflow is present in `.github/workflows/ci.yml`; a successful hosted run has not yet been verified.

## Requirements

- Python 3.12
- The dependencies listed in `requirements.txt`
- A Playwright browser installation for browser-based tests

## Installation

Clone the repository after its public GitHub URL is available, then enter the project directory.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install Chromium for Playwright:

```powershell
python -m playwright install chromium
```

## Configuration

Praman reads YAML configuration organized under an `environments` key.

The repository's `qa-engine.yaml` currently contains example URLs. Replace them with the appropriate URL for your own test environment before running tests against an application.

Example:

```yaml
environments:
  development:
    base_url: "http://127.0.0.1:8000"
    browser: "chromium"
    headless: true
    timeout: 30000
```

The configuration loader requires an environment mapping and a configuration entry for the selected environment.

Supported settings include:

| Setting | Description |
|---|---|
| `base_url` | Base URL for the test environment |
| `browser` | Browser name: `chromium`, `firefox`, or `webkit` |
| `headless` | Whether the browser runs without a visible window |
| `timeout` | Default timeout in milliseconds |
| `version_policy` | Version-policy selection |

`base_url`, `headless`, and `timeout` are required by the current `Settings.from_config()` implementation. The browser defaults to Chromium, and the version policy defaults to `highest`.

## Environment-variable overrides

The configuration environment source recognizes:

| Variable | Purpose |
|---|---|
| `PRAMAN_BASE_URL` | Override the base URL |
| `PRAMAN_BROWSER` | Override the browser |
| `PRAMAN_HEADLESS` | Set headless mode to `true` or `false` |
| `PRAMAN_TIMEOUT` | Override the timeout in milliseconds |
| `PRAMAN_VERSION_POLICY` | Override the version policy |

Environment-variable values are validated as part of the configuration pipeline. Invalid values may cause configuration resolution to fail.

## Pytest browser fixture

The root `conftest.py` defines a `praman_page` fixture.

The fixture requires both `PRAMAN_CONFIG_FILE` and `PRAMAN_ENVIRONMENT`. It loads settings for the selected environment and provides a Playwright page inside a managed browser session.

For example, in PowerShell:

```powershell
$env:PRAMAN_CONFIG_FILE = ".\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
python -m pytest -q
```

The example configuration must be suitable for the tests being run. Browser-based tests require the relevant Playwright browser binaries to be installed.

## Running tests

Run the test suite from the repository root:

```powershell
python -m pytest -q
```

A local run during preparation of this README reported:

```text
476 passed in 10.34s
```

This result records that specific local run; it is not a guarantee that every environment or future revision will produce the same result.

## Project structure

```text
praman/
|-- .github/
|   |-- workflows/
|   |   |-- ci.yml
|-- framework/
|   |-- browser/
|   |-- compatibility/
|   |-- config/
|   |-- contracts/
|-- tests/
|-- conftest.py
|-- qa-engine.yaml
|-- requirements.txt
|-- pytest.ini
|-- LICENSE
|-- README.md

```

## Development status and scope

Praman is a developing framework, not a claim of complete enterprise QA automation.

The repository contains browser-session management, configuration resolution and validation, compatibility-related components, and automated tests. Further work is needed to verify the public CI workflow, define packaging and distribution, and document stable public APIs.

Features such as AI-driven failure analysis, autonomous code fixes, approval workflows, and external service integrations should be considered future capabilities unless and until their implementations and tests are verified in the repository.

## Contributing

Contributions, bug reports, and suggestions are welcome. Before contributing, run the test suite and describe the behavior your change introduces or fixes.

Contribution guidelines and issue templates may be added as the project matures.

## License

Praman is licensed under the MIT License. See [LICENSE](LICENSE) for the full license text.

