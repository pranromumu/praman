# PRAMAN Client Setup Guide

This guide explains how to install PRAMAN in your own project, configure a browser environment, and run automated browser tests using the `praman_page` Pytest fixture.

PRAMAN is designed to be integrated into an existing client project. Your application code and tests remain in your repository; PRAMAN provides the reusable browser automation framework.

## 1. Requirements

Before starting, make sure you have:

- Windows, macOS, or Linux.
- Python 3.12 or newer (required by the current PRAMAN package).
- A client project where you can run Python tests.
- The PRAMAN wheel package provided by the PRAMAN maintainer.
- Access to the application you are authorized to test.

**Important:** PRAMAN is not currently installed from PyPI in this setup. You need the packaged `.whl` file supplied by the maintainer or produced by your organization's release process.

## 2. Create a Python environment

Open PowerShell and navigate to your project directory.

For example:

```powershell
Set-Location "D:\MyClientProject"
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python executable directly instead. For example, replace `python` in the commands below with `.\.venv\Scripts\python.exe`.

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

## 3. Install PRAMAN

Copy the PRAMAN wheel file into a location accessible to your project.

For example, assume the wheel is located at:

`D:\Packages\praman-0.1.0-py3-none-any.whl`

Install it:

```powershell
python -m pip install "D:\Packages\praman-0.1.0-py3-none-any.whl"
```

The PRAMAN wheel declares Playwright and PyYAML as dependencies, so pip should install them automatically when it installs the wheel. Pytest is a separate development/test dependency, so install it in the same virtual environment:

```powershell
python -m pip install pytest
```

Install the Chromium browser binary used by the example configuration. This is a separate step from installing the Playwright Python package:

```powershell
python -m playwright install chromium
```

Check the Python version and confirm that the packages are available in the same environment you will use to run tests:

```powershell
python --version
python -m pip --version
python -m pip show praman pytest playwright PyYAML
```

The installed PRAMAN distribution includes a Pytest plugin that provides the `praman_page` fixture. You do not need to copy PRAMAN's internal source files into your project or add the fixture to your own `conftest.py`.

## 4. Create the configuration file

Create a file named `qa-engine.yaml` in your client project:

```yaml
environments:
  development:
    base_url: "https://example.com"
    browser: "chromium"
    headless: true
    timeout: 30000
```

Replace `https://example.com` with the URL of your authorized test application.

The configuration values mean:

- `base_url`: The base URL configured for your environment.
- `browser`: The browser to use.
- `headless`: Whether the browser runs without a visible window.
- `timeout`: The configured timeout in milliseconds.

The `praman_page` fixture initializes PRAMAN from the selected configuration. It does not automatically navigate the page to `base_url`; your test should explicitly navigate to the page it wants to test.

## 5. Configure environment variables

PRAMAN needs to know which configuration file and environment to load.

In PowerShell, set:

```powershell
$env:PRAMAN_CONFIG_FILE = "D:\MyClientProject\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
```

Replace `D:\MyClientProject` with your actual project directory.

These environment variables apply to the current PowerShell session. Set them again when you open a new session, or configure them in your CI environment.

- `PRAMAN_CONFIG_FILE` identifies the YAML configuration file.
- `PRAMAN_ENVIRONMENT` selects the environment defined in that file.

Both variables are required by the `praman_page` fixture.

## 6. Create your first browser smoke test

Create a folder named `tests` in your client project directory if it does not already exist.

### Test 1: Verify the PRAMAN installation

Create a file named `tests/test_praman_smoke.py`:

```python
def test_praman_smoke(praman_page):
    praman_page.set_content(
        "<title>PRAMAN Smoke Test</title><h1>PRAMAN Ready</h1>"
    )

    assert praman_page.title() == "PRAMAN Smoke Test"
    assert praman_page.locator("h1").inner_text() == "PRAMAN Ready"
```

This smoke test verifies that the installed PRAMAN Pytest plugin provides the `praman_page` fixture and that a browser can start and interact with a page.

It does not require access to a public website or a running application server.

### Test 2: Test your application homepage

After the smoke test passes, create another file named `tests/test_homepage.py`:

```python
def test_homepage(praman_page):
    praman_page.goto("https://your-authorized-test-application.example")

    assert praman_page.locator("h1").is_visible()
```

Replace the example URL with the URL of your authorized test application. Adjust the assertions to match the application's expected behavior.

**Important:** The `praman_page` fixture does not automatically navigate to the configured `base_url`. Each test must explicitly navigate to the page it intends to test.

## 7. Run the tests

From your client project directory, run:

```powershell
python -m pytest -v --tb=short
```

Pytest should discover the test files in the `tests/` directory and execute both tests.

- **Smoke test:** Verifies that the `praman_page` fixture works and that the browser can interact with a page.
- **Homepage test:** Verifies that your authorized test application is reachable and that its homepage contains a visible `h1` element.

If both tests are configured correctly and pass, the test summary should report:

```text
2 passed
```

The homepage test requires a reachable application and a valid test URL. If you have not configured an application yet, you can run only the smoke test:

```powershell
python -m pytest -v --tb=short tests/test_praman_smoke.py
```

The `--tb=short` option keeps failure tracebacks concise while retaining useful diagnostic information.

Pytest discovers the installed PRAMAN plugin through its package entry point. You do not need to import `praman_page` into your test file.

## 8. Reporting and failure evidence

PRAMAN writes a JSON test report when a Pytest session finishes.

By default, the report is written to:

```text
artifacts/praman-report.json
```

The report includes a test summary, the Pytest exit status, and individual test results. Each test result can include its test ID, outcome, duration, failure details, a concise failure message, and a screenshot path.

### Customize the report location

Set `PRAMAN_REPORT_PATH` before running Pytest to choose another report path:

```powershell
$env:PRAMAN_REPORT_PATH = "artifacts/client-test-report.json"
python -m pytest -v
```

PRAMAN creates the report's parent directory if needed.

### Failure screenshots

When a test's execution phase fails and the test uses the `praman_page` fixture, PRAMAN attempts to capture a full-page screenshot.

By default, screenshots are saved under:

```text
artifacts/failures/
```

Set `PRAMAN_ARTIFACTS_DIR` to use a different directory:

```powershell
$env:PRAMAN_ARTIFACTS_DIR = "artifacts/browser-evidence"
python -m pytest -v
```

The report records the screenshot path when capture succeeds. Screenshot capture can fail, so a screenshot is not guaranteed for every failed test.

Keep generated reports and screenshots out of source control when they contain sensitive test data, page content, or other client information. Review the evidence before sharing it.
## 9. Verify plugin discovery

If Pytest reports that the `praman_page` fixture is unavailable, first verify that PRAMAN is installed in the same Python environment used to run Pytest:

```powershell
python -m pip show praman
```

Then inspect the loaded Pytest plugins:

```powershell
python -m pytest --trace-config
```

Look for the PRAMAN plugin in the output.

Make sure you run Pytest using the same virtual environment where you installed PRAMAN.

## 10. Troubleshooting

### Error: `praman_page` fixture not found

Check that:

1. PRAMAN was installed successfully.
2. You are running Pytest from the intended virtual environment.
3. The installed PRAMAN distribution includes its Pytest plugin entry point.

### Error: Missing configuration environment variables

Make sure both variables are set:

```powershell
$env:PRAMAN_CONFIG_FILE = "D:\MyClientProject\qa-engine.yaml"
$env:PRAMAN_ENVIRONMENT = "development"
```

Confirm that the YAML file exists at the specified path and contains the selected environment.

### Error: Browser executable is missing

Install Chromium in the active Python environment:

```powershell
python -m playwright install chromium
```

### Error: Configuration or environment is invalid

Check the YAML indentation and confirm that the value of `PRAMAN_ENVIRONMENT` matches an environment defined in the configuration file.

### Error: The test cannot reach the application

Confirm that the application URL is correct, the application is running, and the machine executing the test has network access to it.

## 11. Client project structure

A typical client project may look like this:

```text
MyClientProject/
|-- .venv/
|-- qa-engine.yaml
`-- tests/
    `-- test_homepage.py
```

The virtual environment is local to your project. Your test files and configuration remain under your control.

## 12. Security and operational notes

- Do not commit passwords, API keys, access tokens, or other secrets to Git.
- Use environment variables or your CI platform's secret-management features for credentials.
- Run tests only against systems you own or are authorized to test.
- Keep the PRAMAN wheel version and Python dependencies consistent across local development and CI.
- The example configuration uses headless Chromium. Your project's requirements may call for a different browser or environment.

## 13. Getting help

When troubleshooting, collect the following information:

- The installed PRAMAN version.
- The Python and Pytest versions.
- The exact error message.
- Whether the error occurs locally or in CI.
- The relevant configuration structure, with all secrets removed.

This information helps diagnose installation, configuration, browser, and test-execution issues without exposing confidential client data.
