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
