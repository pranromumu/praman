# PRAMAN

**A modular Python QA automation framework for browser testing, configuration management, and extensible test integrations.**

PRAMAN provides a reusable foundation for teams and freelance QA engineers who want to integrate browser automation into existing Python test projects. It uses Pytest and Playwright, supports YAML-based environment configuration, and provides an automatically loaded Pytest plugin with the `praman_page` fixture.

PRAMAN is designed to integrate into an existing client repository rather than require a separate, standalone SaaS platform.

> **Development status:** PRAMAN is under active development. The local test suite and an external client test using the installed wheel have passed. A successful hosted GitHub Actions run was recorded for an earlier commit. Broader compatibility, production readiness, and release readiness have not yet been established.

## Current capabilities

- **Browser sessions:** Context-managed Playwright browser-page management.
- **Pytest integration:** Automatically loaded plugin providing the `praman_page` fixture.
- **Environment configuration:** YAML configuration organized by environment.
- **Configuration overrides:** YAML, environment-variable, and command-line configuration sources.
- **Configuration validation:** Validation of required fields, supported browser names, positive timeouts, and version-policy values.
- **Extensible architecture:** Configuration sources, contracts, dependency injection, version negotiation, normalization, and registry-related components.
- **Automated tests:** Tests covering browser sessions, configuration, compatibility, contracts, and related framework behavior.
- **Continuous integration:** A GitHub Actions workflow at `.github/workflows/ci.yml`.

These capabilities describe the current implementation. AI-driven failure analysis, autonomous code fixes, approval workflows, and external service integrations remain future capabilities unless separately implemented and verified.

## Requirements

- Python 3.12 or newer.
- Pytest for running tests.
- Playwright and its required browser binaries for browser-based tests.
- PyYAML for YAML configuration.

The package declares its runtime dependencies in `pyproject.toml`. Pytest is available through the development extra or can be installed separately in a client test environment.

## Installation

There are two primary ways to work with PRAMAN.

### Option 1: Set up the PRAMAN development repository

Use this option if you want to contribute to PRAMAN, modify its source, or run its full test suite.

Clone the repository:

```powershell
git clone https://github.com/pranromumu/praman.git
cd praman
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project in editable mode with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Install the Chromium browser binary:

```powershell
python -m playwright install chromium
```

Run the tests:

```powershell
python -m pytest -q
```

### Option 2: Install PRAMAN in a client project

Use this option when integrating PRAMAN into an existing client-owned repository.

**Current distribution status:** PRAMAN has been built and tested as a wheel, but this README does not claim that the package is published on PyPI. Until a public package release is available, obtain the wheel from your PRAMAN distribution or build process.

Install the wheel into the client's active virtual environment:

```powershell
python -m pip install "C:\path\to\praman-0.1.0-py3-none-any.whl"
```

Install Pytest:

```powershell
python -m pip install "pytest>=9.1.1"
```

Install the required Playwright browser:

```powershell
python -m playwright install chromium
```

Replace the example wheel path with the actual location of the supplied wheel.

Once installed, the Pytest plugin is discovered through the package's registered `pytest11` entry point. Client projects do not need to copy PRAMAN's repository-level `conftest.py` to use the installed `praman_page` fixture.

For the complete client setup instructions, see [CLIENT_SETUP.md](CLIENT_SETUP.md).

## Configuration

PRAMAN uses YAML configuration organized by environment. The development repository includes `qa-engine.yaml` as an example.

Example configuration:

```yaml
environments:
  development:
    base_url: "https://dev.client.com"
    browser: "chromium"
    headless: true
    timeout: 30000

  staging:
    base_url: "https://staging.client.com"
    browser: "chromium"
    headless: true
    timeout: 30000

  production:
    base_url: "https://client.com"
    browser: "chromium"
    headless: true
    timeout: 30000
```

These URLs are examples. Replace them with authorized target environments before running tests. Production testing should only be performed with explicit authorization and appropriate safeguards.

### Configuration settings

| Setting | Purpose |
|---|---|
| `base_url` | Base URL for the target environment |
| `browser` | Browser selection; Chromium is the default |
| `headless` | Whether the browser runs without a visible window |
| `timeout` | Default browser-operation timeout in milliseconds |
| `version_policy` | Policy used by the compatibility and version-selection layer |

### Configuration validation

PRAMAN loads the selected environment from the `environments` mapping in the YAML configuration file. The configuration source checks that the file exists, can be parsed, and contains a mapping for the requested environment. The settings layer then validates the resulting configuration.

The current settings layer validates:

- **Required settings:** `base_url`, `headless`, and `timeout`.
- **Browser:** Defaults to `chromium`; supported values are `chromium`, `firefox`, and `webkit`.
- **Headless mode:** Must be a Boolean.
- **Timeout:** Must be a positive integer in milliseconds.
- **Version policy:** Defaults to `highest`. When a policy-name provider is used, the configured name must be supported by that provider.

Unknown configuration fields and missing required fields produce validation errors.

### Configuration precedence

The standard configuration pipeline merges sources in this order:

1. YAML configuration â€” required.
2. Environment variables â€” optional.
3. Command-line arguments â€” optional.

When multiple sources define the same setting, later sources override earlier ones. Failures from the required YAML source propagate; optional-source failures are logged and skipped.

### Command-line arguments

The CLI configuration source recognizes these arguments:

- `--base-url`
- `--browser`
- `--headless` â€” accepts `true` or `false`, case-insensitively.
- `--timeout` â€” expects an integer.
- `--version-policy`

The CLI source uses `parse_known_args()` so it can coexist with other command-line arguments. Invalid values are rejected by the relevant parsing or configuration-validation logic.

### Environment variables for settings

The settings layer recognizes these environment-variable names:

- `PRAMAN_BASE_URL`
- `PRAMAN_BROWSER`
- `PRAMAN_HEADLESS`
- `PRAMAN_TIMEOUT`
- `PRAMAN_VERSION_POLICY`

These settings variables are distinct from the two environment variables required to configure the `praman_page` fixture.

## Pytest integration

PRAMAN registers an automatically loaded Pytest plugin:

```text
framework.pytest_plugin
```

The plugin provides the `praman_page` fixture. It reads two environment variables:

- `PRAMAN_CONFIG_FILE` â€” the path to the YAML configuration file.
- `PRAMAN_ENVIRONMENT` â€” the environment key to load from that file.

### Configure the fixture on Windows

For example, in PowerShell:

```powershell
$env:PRAMAN_CONFIG_FILE = "D:\client-project\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
```

Update these paths and the environment name to match the client project.

### Example client test

Create a test file such as `tests/test_homepage.py`:

```python
def test_homepage(praman_page):
    praman_page.goto("https://example.com")

    assert praman_page.title()
```

Replace `https://example.com` with an authorized test target.

Run the test from the client repository:

```powershell
python -m pytest -v
```

Pytest should discover the installed plugin and make `praman_page` available without a client-level copy of PRAMAN's root `conftest.py`.

The fixture creates a browser page using the selected configuration and manages its browser-session lifecycle. Tests can interact with the returned Playwright page using normal Playwright APIs.

If the required environment variables are missing, the fixture raises a Pytest usage error explaining which values must be configured.

> **Important:** The root-level `conftest.py` in the PRAMAN development repository also provides a fixture for repository tests. The installed plugin is the integration mechanism intended for external client projects.

### API testing

The installed PRAMAN Pytest plugin provides the `praman_api` fixture, backed by PRAMAN's `ApiClient` abstraction and Playwright.

Supported methods include `get()`, `post()`, `put()`, `patch()`, and `delete()`. Request options are forwarded to Playwright, and responses retain the Playwright `APIResponse` interface.

See [API_TESTING.md](API_TESTING.md) for configuration, authentication, and usage examples.

### Failure screenshots

PRAMAN automatically attempts to capture a full-page screenshot when a test using the `praman_page` fixture fails during execution.

By default, screenshots are saved to:

```text
artifacts/failures/
```

To use a custom output directory, set the `PRAMAN_ARTIFACTS_DIR` environment variable. For example, in PowerShell:

```powershell
$env:PRAMAN_ARTIFACTS_DIR = "D:\client-project\test-artifacts"
```

PRAMAN creates the output directory if it does not exist. If screenshot capture fails, PRAMAN reports the error without masking the original test failure. API-only tests that do not use `praman_page` do not trigger screenshot capture.


## JSON test evidence report

PRAMAN generates a JSON report at the end of each pytest session. The report includes:

- Summary counts for total, passed, failed, and skipped tests.
- Test IDs and individual outcomes.
- Test durations in seconds.
- Failure details when available.
- Failure screenshot paths when captured.
- Pytest exit status.
- Report generation timestamp in UTC.

By default, the report is written to `artifacts/praman-report.json`.

To use a custom report path in PowerShell:

```powershell
$env:PRAMAN_REPORT_PATH = "artifacts/reports/test-report.json"
python -m pytest -q
```

PRAMAN creates the report directory if it does not exist. If report generation fails, PRAMAN prints an error message without replacing the original pytest exit status.


## Running the PRAMAN test suite

From the PRAMAN development repository, with the development dependencies installed:

```powershell
python -m pytest -q
```

### Recorded verification

The following results have been observed during development:

- **Local repository test suite:** 579 tests passed in the latest verified local run on 2026-10-30, using both `python -m pytest -q` and `pytest -q`.
- **Source-distribution test suite:** 542 tests passed in the latest rebuilt source-distribution run.
- **External client tests:** 2 tests passed using the installed wheel in an isolated Python environment.
- **Plugin discovery:** Pytest reported `praman-0.1.0` when running the external client test.
- **Hosted CI:** A successful GitHub Actions run was recorded for the earlier commit `5dbe6319bb5e2b99979e52f5a8fa5b2f8b35c9c9`.

The external wheel test validates the packaged plugin and fixture in that test environment. The hosted CI result predates the plugin commit and does not establish that the latest commit has passed hosted CI.

These are recorded test results, not guarantees that every environment, browser version, or future run will behave identically.

## Continuous integration

The workflow at `.github/workflows/ci.yml` runs on GitHub-hosted Ubuntu runners. It checks out the repository, sets up Python 3.12, installs dependencies, installs Chromium, and runs the Pytest suite.

The workflow is configured for pushes and pull requests targeting `main`, as well as manual dispatch.

A successful run on an earlier commit does not automatically verify subsequent changes. Each relevant change should be validated by its own test run or workflow result.

## Project structure

The following is a high-level view of the main repository components:

```text
praman/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- framework/
|   |-- browser/
|   |-- compatibility/
|   |-- config/
|   |-- contracts/
|   `-- pytest_plugin.py
|-- tests/
|-- conftest.py
|-- qa-engine.yaml
|-- requirements.txt
|-- pytest.ini
|-- pyproject.toml
|-- MANIFEST.in
|-- LICENSE
|-- README.md
`-- CLIENT_SETUP.md
```

Individual files and local development artifacts may vary. The `framework` package contains the reusable implementation, while the repository's `tests` directory contains the development test suite.

## Development scope and roadmap

PRAMAN is an evolving framework, not a claim of a fully autonomous enterprise QA platform. Its current focus is a testable foundation for browser automation, configuration management, and extensible integration contracts.

Potential future development includes:

- Evidence-grounded AI analysis of test failures.
- AI-assisted test creation.
- Suggested code changes with human review.
- Controlled reruns and approval workflows.
- Integrations with source-control, issue-tracking, notification, and artifact-storage systems.
- Improved client installation, packaging, and release workflows.

These are roadmap items unless their implementation and behavior are independently verified.

## Contributing

Contributions, bug reports, and reproducible test cases are welcome.

When reporting an issue, include the relevant Python version, operating system, reproduction steps, and error output. Avoid including credentials, access tokens, private client data, or other sensitive information.

## License

PRAMAN is distributed under the MIT License. See [LICENSE](LICENSE) for details.
