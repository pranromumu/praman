
import pytest

from framework.api.authentication import build_api_headers
from framework.config.api_settings import ApiSettings


def bearer_settings():
    return ApiSettings.from_config(
        {
            "headers": {
                "X-Client": "praman",
            },
            "authentication": {
                "type": "bearer",
                "token_env": "PRAMAN_API_TOKEN",
            },
        }
    )


def test_build_api_headers_without_authentication():
    settings = ApiSettings.from_config(
        {
            "headers": {
                "X-Client": "praman",
            }
        }
    )

    headers = build_api_headers(settings)

    assert headers == {
        "X-Client": "praman",
    }


def test_build_api_headers_adds_bearer_token(monkeypatch):
    monkeypatch.setenv("PRAMAN_API_TOKEN", "test-secret-token")

    headers = build_api_headers(bearer_settings())

    assert headers == {
        "X-Client": "praman",
        "Authorization": "Bearer test-secret-token",
    }


def test_build_api_headers_rejects_missing_token(monkeypatch):
    monkeypatch.delenv("PRAMAN_API_TOKEN", raising=False)

    with pytest.raises(ValueError, match="environment variable"):
        build_api_headers(bearer_settings())


def test_build_api_headers_rejects_empty_token(monkeypatch):
    monkeypatch.setenv("PRAMAN_API_TOKEN", "   ")

    with pytest.raises(ValueError, match="empty"):
        build_api_headers(bearer_settings())


def test_build_api_headers_rejects_newline_in_token(monkeypatch):
    monkeypatch.setenv("PRAMAN_API_TOKEN", "secret\r\nInjected: value")

    with pytest.raises(ValueError, match="newline"):
        build_api_headers(bearer_settings())


def test_build_api_headers_does_not_expose_token_in_error(monkeypatch):
    secret = "secret-value-that-must-not-leak"

    monkeypatch.setenv(
        "PRAMAN_API_TOKEN",
        f"{secret}\r\nInjected: value",
    )

    with pytest.raises(ValueError) as error:
        build_api_headers(bearer_settings())

    assert secret not in str(error.value)