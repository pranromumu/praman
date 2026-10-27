import pytest

from framework import pytest_plugin


def test_praman_page_requires_both_environment_variables(monkeypatch):
    monkeypatch.delenv("PRAMAN_CONFIG_FILE", raising=False)
    monkeypatch.delenv("PRAMAN_ENVIRONMENT", raising=False)

    with pytest.raises(
        pytest.UsageError,
        match="Set both PRAMAN_CONFIG_FILE and PRAMAN_ENVIRONMENT",
    ):
        next(pytest_plugin.praman_page.__wrapped__())


def test_praman_page_reports_missing_config_file_as_usage_error(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("PRAMAN_CONFIG_FILE", str(tmp_path / "missing.yaml"))
    monkeypatch.setenv("PRAMAN_ENVIRONMENT", "development")

    with pytest.raises(
        pytest.UsageError,
        match="PRAMAN configuration error:.*Praman configuration file not found",
    ):
        next(pytest_plugin.praman_page.__wrapped__())


def test_praman_page_reports_unsupported_environment_as_usage_error(
    monkeypatch, tmp_path
):
    config_file = tmp_path / "qa-engine.yaml"
    config_file.write_text(
        "environments:\n  development:\n    base_url: 'http://127.0.0.1'\n"
        "    browser: chromium\n    headless: true\n    timeout: 5000\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PRAMAN_CONFIG_FILE", str(config_file))
    monkeypatch.setenv("PRAMAN_ENVIRONMENT", "unknown")

    with pytest.raises(
        pytest.UsageError,
        match="PRAMAN configuration error:.*Unsupported environment",
    ):
        next(pytest_plugin.praman_page.__wrapped__())


def test_capture_failure_screenshot_uses_configured_directory(
    monkeypatch, tmp_path
):
    import hashlib
    from unittest.mock import Mock

    artifacts_dir = tmp_path / "custom-artifacts"
    monkeypatch.setenv(
        "PRAMAN_ARTIFACTS_DIR",
        str(artifacts_dir),
    )

    node_id = "tests/test_checkout.py::test payment fails"
    expected_hash = hashlib.sha256(
        node_id.encode("utf-8")
    ).hexdigest()[:10]

    page = Mock()

    screenshot_path = pytest_plugin._capture_failure_screenshot(
        page,
        node_id,
    )

    assert screenshot_path == (
        artifacts_dir
        / f"tests_test_checkout.py_test_payment_fails_{expected_hash}.png"
    )
    assert screenshot_path.parent == artifacts_dir

    page.screenshot.assert_called_once_with(
        path=str(screenshot_path),
        full_page=True,
    )

def test_build_json_report_counts_test_outcomes():
    results = [
        {"outcome": "passed"},
        {"outcome": "passed"},
        {"outcome": "failed"},
        {"outcome": "skipped"},
    ]

    report = pytest_plugin._build_json_report(results, exit_status=1)

    assert report["summary"] == {
        "total": 4,
        "passed": 2,
        "failed": 1,
        "skipped": 1,
    }
    assert report["exit_status"] == 1
    assert report["tests"] == results


def test_build_json_report_handles_empty_results():
    report = pytest_plugin._build_json_report([], exit_status=0)

    assert report["summary"] == {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert report["exit_status"] == 0
    assert report["tests"] == []

def test_write_json_report_creates_report_file(
    monkeypatch, tmp_path
):
    import json
    from types import SimpleNamespace

    report_path = tmp_path / "reports" / "praman-report.json"
    monkeypatch.setenv("PRAMAN_REPORT_PATH", str(report_path))

    session = SimpleNamespace(
        config=SimpleNamespace(
            _praman_test_results=[
                {
                    "test_id": "test_example",
                    "outcome": "passed",
                    "duration_seconds": 0.1,
                    "failure_details": None,
                    "screenshot_path": None,
                }
            ]
        )
    )

    pytest_plugin.pytest_sessionfinish(session, exitstatus=0)

    saved_report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert saved_report["summary"]["total"] == 1
    assert saved_report["summary"]["passed"] == 1
    assert saved_report["exit_status"] == 0
    assert saved_report["tests"][0]["test_id"] == "test_example"
    assert saved_report["generated_at"].endswith("+00:00")


def test_write_json_report_handles_write_error(
    monkeypatch, tmp_path, capsys
):
    from pathlib import Path
    from types import SimpleNamespace

    report_path = tmp_path / "praman-report.json"
    monkeypatch.setenv("PRAMAN_REPORT_PATH", str(report_path))

    def fail_write(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr(Path, "write_text", fail_write)

    session = SimpleNamespace(
        config=SimpleNamespace(_praman_test_results=[])
    )

    pytest_plugin.pytest_sessionfinish(session, exitstatus=1)

    captured = capsys.readouterr()
    assert "PRAMAN could not write JSON report" in captured.out
    assert "Permission denied" in captured.out

def test_screenshot_error_does_not_hide_original_test_failure(
    monkeypatch, capsys
):
    from types import SimpleNamespace
    from unittest.mock import Mock

    page = Mock()
    item = SimpleNamespace(
        funcargs={"praman_page": page},
        nodeid="tests/test_checkout.py::test_checkout",
        _praman_phase_reports={},
        config=SimpleNamespace(_praman_test_results=[]),
    )

    monkeypatch.setattr(
        pytest_plugin,
        "_capture_failure_screenshot",
        Mock(side_effect=OSError("Browser already closed")),
    )

    report = SimpleNamespace(
        when="call",
        failed=True,
        longrepr="Checkout total was incorrect",
        duration=0.1,
        skipped=False,
    )

    outcome = SimpleNamespace(get_result=lambda: report)
    hook = pytest_plugin.pytest_runtest_makereport(
        item, SimpleNamespace()
    )

    next(hook)

    with pytest.raises(StopIteration):
        hook.send(outcome)

    captured = capsys.readouterr()
    assert "PRAMAN could not capture failure screenshot" in captured.out
    assert "Browser already closed" in captured.out
    assert report.failed is True
    assert not hasattr(item, "_praman_screenshot_path")

def test_setup_failure_is_recorded_in_json_results():
    from types import SimpleNamespace

    item = SimpleNamespace(
        nodeid="tests/test_checkout.py::test_checkout",
        _praman_phase_reports={},
        config=SimpleNamespace(_praman_test_results=[]),
    )

    setup_report = SimpleNamespace(
        when="setup",
        failed=True,
        skipped=False,
        longrepr="Browser fixture failed to initialize",
        duration=0.2,
    )

    teardown_report = SimpleNamespace(
        when="teardown",
        failed=False,
        skipped=False,
        longrepr=None,
        duration=0.01,
    )

    item._praman_phase_reports["setup"] = setup_report

    hook = pytest_plugin.pytest_runtest_makereport(
        item, SimpleNamespace()
    )
    next(hook)

    with pytest.raises(StopIteration):
        hook.send(
            SimpleNamespace(get_result=lambda: teardown_report)
        )

    results = item.config._praman_test_results

    assert len(results) == 1
    assert results[0]["test_id"] == item.nodeid
    assert results[0]["outcome"] == "failed"
    assert "Browser fixture failed to initialize" in (
        results[0]["failure_details"]
    )


def test_capture_failure_screenshot_avoids_filename_collisions(
    monkeypatch, tmp_path
):
    from unittest.mock import Mock

    monkeypatch.setenv("PRAMAN_ARTIFACTS_DIR", str(tmp_path))

    first_path = pytest_plugin._capture_failure_screenshot(
        Mock(),
        "tests/test a.py::test_example",
    )
    second_path = pytest_plugin._capture_failure_screenshot(
        Mock(),
        "tests/test@a.py::test_example",
    )

    assert first_path != second_path

def test_teardown_failure_is_recorded_in_json_results():
    from types import SimpleNamespace

    item = SimpleNamespace(
        nodeid="tests/test_checkout.py::test_checkout",
        _praman_phase_reports={},
        config=SimpleNamespace(_praman_test_results=[]),
    )

    call_report = SimpleNamespace(
        when="call",
        failed=False,
        skipped=False,
        longrepr=None,
        duration=0.1,
    )

    teardown_report = SimpleNamespace(
        when="teardown",
        failed=True,
        skipped=False,
        longrepr="RuntimeError: Browser cleanup failed",
        duration=0.02,
    )

    item._praman_phase_reports["call"] = call_report

    hook = pytest_plugin.pytest_runtest_makereport(
        item, SimpleNamespace()
    )
    next(hook)

    with pytest.raises(StopIteration):
        hook.send(
            SimpleNamespace(get_result=lambda: teardown_report)
        )

    results = item.config._praman_test_results

    assert len(results) == 1
    assert results[0]["test_id"] == item.nodeid
    assert results[0]["outcome"] == "failed"
    assert "TEARDOWN FAILURE" in results[0]["failure_details"]
    assert "Browser cleanup failed" in results[0]["failure_details"]
