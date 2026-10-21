
import pytest

from framework.browser.session import open_browser_page
from framework.config.settings import Settings


def test_browser_page_renders_local_html():
    settings = Settings(
        BASE_URL="http://local.test",
        HEADLESS=True,
        TIMEOUT=5000,
    )

    with open_browser_page(settings) as page:
        page.set_content(
            "<title>Praman Local Check</title><h1>Ready</h1>"
        )

        assert page.title() == "Praman Local Check"
        assert page.locator("h1").inner_text() == "Ready"


def test_browser_context_exits_when_exception_occurs():
    settings = Settings(
        BASE_URL="http://local.test",
        HEADLESS=True,
        TIMEOUT=5000,
    )

    with pytest.raises(
        RuntimeError,
        match="intentional test error",
    ):
        with open_browser_page(settings):
            raise RuntimeError("intentional test error")


def test_invalid_browser_is_rejected_before_launch():
    settings = Settings(
        BASE_URL="http://local.test",
        BROWSER="safari",
        HEADLESS=True,
        TIMEOUT=5000,
    )

    with pytest.raises(
        ValueError,
        match="BROWSER must be one of",
    ):
        with open_browser_page(settings):
            pass


@pytest.fixture
def local_praman_config(monkeypatch, tmp_path):
    config_file = tmp_path / "qa-engine.local-test.yaml"

    config_file.write_text(
        """
environments:
  development:
    base_url: "http://local.test"
    browser: "chromium"
    headless: true
    timeout: 5000
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PRAMAN_CONFIG_FILE", str(config_file))
    monkeypatch.setenv("PRAMAN_ENVIRONMENT", "development")

def test_pytest_fixture_provides_browser_page(local_praman_config, praman_page):
    praman_page.set_content(
        "<title>Praman Fixture Check</title><h1>Fixture Ready</h1>"
    )

    assert praman_page.title() == "Praman Fixture Check"
    assert praman_page.locator("h1").inner_text() == "Fixture Ready"


def test_pytest_fixture_rejects_incomplete_configuration(
    monkeypatch,
    request,
):
    monkeypatch.setenv(
        "PRAMAN_CONFIG_FILE",
        ".\\qa-engine.yaml",
    )
    monkeypatch.delenv(
        "PRAMAN_ENVIRONMENT",
        raising=False,
    )

    with pytest.raises(
        pytest.UsageError,
        match="Set both PRAMAN_CONFIG_FILE and PRAMAN_ENVIRONMENT",
    ):
        request.getfixturevalue("praman_page")


