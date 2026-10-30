from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


class ApiClient:
    """PRAMAN API client that delegates HTTP requests to Playwright."""

    def __init__(self, context: APIRequestContext) -> None:
        self._context = context

    def get(self, url: str, **kwargs: Any) -> APIResponse:
        return self._context.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> APIResponse:
        return self._context.post(url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> APIResponse:
        return self._context.put(url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> APIResponse:
        return self._context.patch(url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> APIResponse:
        return self._context.delete(url, **kwargs)