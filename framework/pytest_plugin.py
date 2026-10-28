import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from framework.api.session import open_api_session
from framework.browser.session import open_browser_page
from framework.config.environment import Environment
from framework.config.settings import Settings


_REPORT_METADATA = None


def _extract_failure_message(failure_details):
    """Extract a concise failure message from structured failure details."""
    if not failure_details:
        return None

    lines = [
        line.strip()
        for line in failure_details.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    for line in reversed(lines):
        if line.startswith("E "):
            return line[2:].strip()

    return lines[-1]


def _build_json_report(results, exit_status, metadata=None):
    """Build a structured JSON-compatible test report."""
    outcomes = [result["outcome"] for result in results]

    report = {
        "summary": {
            "total": len(results),
            "passed": outcomes.count("passed"),
            "failed": outcomes.count("failed"),
            "skipped": outcomes.count("skipped"),
        },
        "exit_status": exit_status,
        "tests": results,
    }

    if metadata is not None:
        report["metadata"] = metadata

    return report


def _load_settings() -> Settings:
    """Load validated settings from the configured environment."""

    config_file = os.environ.get("PRAMAN_CONFIG_FILE")
    environment_name = os.environ.get("PRAMAN_ENVIRONMENT")

    if not config_file or not environment_name:
        raise pytest.UsageError(
            "Set both PRAMAN_CONFIG_FILE and PRAMAN_ENVIRONMENT "
            "to use Praman fixtures."
        )

    global _REPORT_METADATA

    try:
        environment = Environment.from_string(environment_name)
        settings = Settings.from_config_file(
            file_path=config_file,
            env=environment,
        )

        _REPORT_METADATA = {
            "browser": settings.BROWSER,
            "environment": environment.value,
        }

        return settings

    except (OSError, ValueError) as exc:
        raise pytest.UsageError(
            f"PRAMAN configuration error: {exc}"
        ) from exc


def _capture_failure_screenshot(page, node_id: str) -> Path:
    """Save a full-page screenshot for a failed test."""

    import hashlib

    artifacts_dir = Path(
        os.environ.get(
            "PRAMAN_ARTIFACTS_DIR",
            "artifacts/failures",
        )
    )
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    safe_node_id = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        node_id,
    ).strip("._") or "failed-test"

    node_id_hash = hashlib.sha256(
        node_id.encode("utf-8")
    ).hexdigest()[:10]

    screenshot_path = (
        artifacts_dir / f"{safe_node_id}_{node_id_hash}.png"
    )
    page.screenshot(path=str(screenshot_path), full_page=True)

    return screenshot_path


@pytest.fixture
def praman_page():
    """Provide a browser page using explicit Praman configuration."""

    settings = _load_settings()

    with open_browser_page(settings) as page:
        yield page


@pytest.fixture
def praman_api():
    """Provide an API request context using explicit Praman configuration."""

    settings = _load_settings()

    with open_api_session(
        settings.BASE_URL,
        timeout=settings.TIMEOUT,
    ) as api:
        yield api


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect test phases and capture browser evidence on call failures."""

    outcome = yield
    report = outcome.get_result()

    phase_reports = getattr(item, "_praman_phase_reports", {})
    phase_reports[report.when] = report
    item._praman_phase_reports = phase_reports

    if report.when == "call" and report.failed:
        page = item.funcargs.get("praman_page")

        if page is not None:
            try:
                screenshot_path = _capture_failure_screenshot(
                    page,
                    item.nodeid,
                )
                item._praman_screenshot_path = str(screenshot_path)
                print(f"\nPRAMAN failure screenshot: {screenshot_path}")

            except Exception as exc:
                print(
                    f"\nPRAMAN could not capture failure screenshot: {exc}"
                )

    if report.when != "teardown":
        return

    setup_report = phase_reports.get("setup")
    call_report = phase_reports.get("call")
    teardown_report = phase_reports.get("teardown")

    reports = [
        phase
        for phase in (setup_report, call_report, teardown_report)
        if phase is not None
    ]

    failed_reports = [
        phase for phase in reports if phase.failed
    ]

    if failed_reports:
        final_outcome = "failed"
    elif any(phase.skipped for phase in reports):
        final_outcome = "skipped"
    else:
        final_outcome = "passed"

    failure_details = "\n\n".join(
        f"{phase.when.upper()} FAILURE:\n{phase.longrepr}"
        for phase in failed_reports
    ) or None

    failure_message = _extract_failure_message(failure_details)
    results = item.config._praman_test_results

    results.append(
        {
            "test_id": item.nodeid,
            "outcome": final_outcome,
            "duration_seconds": round(
                sum(phase.duration for phase in reports),
                3,
            ),
            "failure_details": failure_details,
            "failure_message": failure_message,
            "screenshot_path": getattr(
                item,
                "_praman_screenshot_path",
                None,
            ),
        }
    )


def pytest_sessionstart(session):
    """Initialize report collection for this test session."""

    global _REPORT_METADATA
    _REPORT_METADATA = None

    session.config._praman_test_results = []


def pytest_sessionfinish(session, exitstatus):
    """Write the JSON evidence report when the test session ends."""

    report_path = Path(
        os.environ.get(
            "PRAMAN_REPORT_PATH",
            "artifacts/praman-report.json",
        )
    )

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = _build_json_report(
            session.config._praman_test_results,
            exitstatus,
            metadata=_REPORT_METADATA,
        )

        report["generated_at"] = datetime.now(timezone.utc).isoformat()

        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        print(f"\nPRAMAN JSON report: {report_path}")

    except Exception as exc:
        print(f"\nPRAMAN could not write JSON report: {exc}")
