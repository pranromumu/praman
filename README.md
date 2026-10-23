# Praman

**A modular Python QA automation framework built around configuration management, browser automation, and extensible integration contracts.**

Praman provides a foundation for managing test configuration and running browser-based tests with Pytest and Playwright.

> **Development status:** Praman is under active development. The local test suite, hosted GitHub Actions run, wheel installation, dependency consistency, and packaged source-distribution tests have been verified. Broader compatibility and release readiness have not yet been established.

## Current capabilities

- **Browser sessions:** A context-managed Playwright browser-page helper.
- **Pytest integration:** A `praman_page` fixture that loads explicit configuration and provides a browser page to tests.
- **Environment configuration:** YAML configuration organized by environment.
- **Configuration overrides:** YAML, environment-variable, and command-line configuration sources.
- **Validation:** Checks for required configuration fields, supported browser names, positive timeouts, and version-policy values.
- **Extensible architecture:** Source contracts, dependency injection, version negotiation, normalization, and registry-related components.
- **Automated tests:** Tests covering browser sessions, configuration, compatibility, contracts, and related framework behavior.
- **Continuous integration:** A GitHub Actions workflow at `.github/workflows/ci.yml`; a successful hosted run was recorded for an earlier commit and does not verify the current uncommitted changes.

These capabilities describe the current codebase. AI-driven failure analysis, autonomous code fixes, approval workflows, and external service integrations should be treated as future capabilities unless separately implemented and verified.

## Requirements

- Python 3.12 or newer
- Dependencies listed in `requirements.txt`
- Playwright browser binaries for browser-based tests

## Installation

Clone the public repository:

```powershell
git clone https://github.com/pranromumu/praman.git
cd praman
```

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

Praman uses YAML configuration organized by environment. The repository includes `qa-engine.yaml` as an example configuration file.

Example structure:

```yaml
environments:
  development:
    base_url: "https://dev.client.com"
    headless: false
    timeout: 30000
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
  production:
    base_url: "https://client.com"
    headless: true
    timeout: 30000
```

**Important:** The URLs above are examples. Replace them with authorized target environments before running browser tests.

The settings layer supports these configuration values:

| Setting | Purpose |
|---|---|
| `base_url` | Base URL for the target environment |
| `browser` | Browser selection; Chromium is the default |
| `headless` | Whether the browser runs without a visible window |
| `timeout` | Default browser operation timeout in milliseconds |
| `version_policy` | Policy used by the compatibility/version-selection layer |

### Configuration validation

Praman loads the selected environment from the `environments` mapping in `qa-engine.yaml`. The YAML source checks that the file exists, can be parsed, and contains a configuration mapping for the requested environment. The settings layer then validates the merged configuration values.

After configuration sources are merged, the settings layer validates the resulting configuration:

- **Required:** `base_url`, `headless`, and `timeout`.
- **Browser:** Defaults to `chromium`; supported values are `chromium`, `firefox`, and `webkit`.
- **Headless mode:** Must be a Boolean.
- **Timeout:** Must be a positive integer, in milliseconds.
- **Version policy:** Defaults to `highest`. When a policy-name provider is used, the configured name must be supported by that provider.

Unknown configuration fields and missing required fields produce validation errors.

### Configuration precedence

The standard configuration pipeline merges sources in this order:

1. YAML configuration (required).
2. Environment variables (optional).
3. Command-line arguments (optional).

When multiple sources define the same setting, the later source overrides the earlier value. Failures from the required YAML source propagate; optional-source failures are logged and skipped.

### Command-line arguments

The CLI source recognizes these arguments:

- `--base-url`
- `--browser`
- `--headless`: accepts `true` or `false`, case-insensitively.
- `--timeout`: expects an integer.
- `--version-policy`

The CLI source uses `parse_known_args()` so it can coexist with other command-line arguments. Invalid values are rejected by the relevant parsing or configuration-validation logic.


### Environment variables

The settings layer recognizes these environment-variable names:

- `PRAMAN_BASE_URL`
- `PRAMAN_BROWSER`
- `PRAMAN_HEADLESS`
- `PRAMAN_TIMEOUT`
- `PRAMAN_VERSION_POLICY`

### Pytest fixture configuration

The root-level `conftest.py` provides the `praman_page` fixture. It expects:

- `PRAMAN_CONFIG_FILE` - the path to the YAML configuration file.
- `PRAMAN_ENVIRONMENT` - the environment key to load from that file.

Set these variables before running tests that use the fixture. The fixture is currently defined in the repository's root `conftest.py`; it is not claimed to be an independently installed pytest plugin.

## Running the tests

From the repository root, with the project dependencies installed:

```powershell
python -m pytest -q
```

**Latest recorded local verification:** 476 tests passed.

**Hosted CI verification:** A successful GitHub Actions run was recorded for the earlier commit `5dbe6319bb5e2b99979e52f5a8fa5b2f8b35c9c9`. This run predates the current uncommitted changes and does not verify the current working tree.

These results document specific runs, not a guarantee that every future environment or run will produce the same result.

## Continuous integration

The workflow at `.github/workflows/ci.yml` runs on GitHub-hosted Ubuntu runners. It checks out the repository, sets up Python 3.12, installs dependencies, installs Chromium, and runs the Pytest suite.

The workflow is configured for pushes and pull requests targeting `main`, as well as manual dispatch.

## Project structure

```text
praman/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- framework/
|   |-- browser/
|   |-- compatibility/
|   |-- config/
|   `-- contracts/
|-- tests/
|-- conftest.py
|-- qa-engine.yaml
|-- requirements.txt
|-- pytest.ini
|-- pyproject.toml
|-- MANIFEST.in
|-- LICENSE
`-- README.md
```

This is a high-level view of the main tracked project components. Individual files and local development artifacts may vary.

## Development scope

Praman is an evolving framework, not a claim of a fully autonomous enterprise QA platform. Its current focus is a testable foundation for browser automation, configuration management, and extensible integration contracts.

Potential future development includes:

- Evidence-grounded AI analysis of test failures
- AI-assisted test creation
- Suggested code changes with human review
- Controlled reruns and approval workflows
- Integrations with source-control, issue-tracking, notification, and artifact-storage systems

These are roadmap items unless their implementation and behavior are independently verified.

## Contributing

Contributions, bug reports, and reproducible test cases are welcome. Please describe the environment, steps to reproduce the issue, and relevant error output. Avoid including credentials, access tokens, private client data, or other sensitive information in reports.

## License

Praman is distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
