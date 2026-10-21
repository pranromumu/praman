from contextlib import contextmanager
from collections.abc import Iterator

from playwright.sync_api import Page, sync_playwright

from framework.config.settings import Settings


@contextmanager
def open_browser_page(settings: Settings) -> Iterator[Page]:
    """Open a Playwright page using validated Praman settings."""
    settings.validate()

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.BROWSER)
        browser = browser_type.launch(headless=settings.HEADLESS)

        try:
            page = browser.new_page()
            page.set_default_timeout(settings.TIMEOUT)
            yield page
        finally:
            browser.close()
