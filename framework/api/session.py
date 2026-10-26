
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import urlsplit

from playwright.sync_api import APIRequestContext, sync_playwright


@contextmanager
def open_api_session(
    base_url: str,
    timeout: int = 30000,
) -> Iterator[APIRequestContext]:
    """Open a Playwright API request context with validated settings."""
    if not isinstance(base_url, str) or not base_url.strip():
        raise ValueError("base_url must be a non-empty string.")

    try:
        parsed_url = urlsplit(base_url.strip())
        valid_url = (
            parsed_url.scheme in {"http", "https"}
            and bool(parsed_url.hostname)
            and parsed_url.port != 0
        )
    except ValueError:
        valid_url = False

    if not valid_url:
        raise ValueError(
            "base_url must be an absolute HTTP or HTTPS URL with a hostname."
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("timeout must be an integer greater than 0.")

    with sync_playwright() as playwright:
        api_context = playwright.request.new_context(
            base_url=base_url.strip().rstrip("/"),
            timeout=timeout,
        )
        try:
            yield api_context
        finally:
            api_context.dispose()
