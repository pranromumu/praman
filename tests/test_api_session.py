
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import MagicMock

import pytest

from framework.api.session import open_api_session


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps(
                {"status": "ok", "service": "praman"}
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/headers":
            body = json.dumps(
                {
                    "x_client": self.headers.get("X-Client"),
                    "authorization": self.headers.get("Authorization"),
                }
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        pass


@pytest.fixture
def local_api_server():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        HealthHandler,
    )
    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.parametrize(
    "base_url",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_api_session_rejects_invalid_base_url(base_url):
    with pytest.raises(
        ValueError,
        match="base_url must be a non-empty string",
    ):
        with open_api_session(base_url):
            pass


@pytest.mark.parametrize(
    "base_url",
    [
        "not-a-url",
        "ftp://example.com",
        "http:///missing-host",
        "http://example.com:99999",
    ],
)
def test_api_session_rejects_malformed_base_url(base_url):
    with pytest.raises(
        ValueError,
        match="base_url must be an absolute HTTP or HTTPS URL with a hostname",
    ):
        with open_api_session(base_url):
            pass


@pytest.mark.parametrize(
    "timeout",
    [
        0,
        -1,
        True,
        False,
        1.5,
        "30000",
        None,
    ],
)
def test_api_session_rejects_invalid_timeout(timeout):
    with pytest.raises(
        ValueError,
        match="timeout must be an integer greater than 0",
    ):
        with open_api_session("http://127.0.0.1", timeout=timeout):
            pass


def test_api_session_get_health_endpoint(local_api_server):
    with open_api_session(local_api_server) as api:
        response = api.get("/health")

        assert response.status == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json() == {
            "status": "ok",
            "service": "praman",
        }


def test_api_session_handles_not_found(local_api_server):
    with open_api_session(local_api_server) as api:
        response = api.get("/missing")

        assert response.status == 404
        assert "Not Found" in response.text()


def test_pytest_fixture_provides_api_context(
    monkeypatch,
    tmp_path,
    local_api_server,
    request,
):
    config_file = tmp_path / "qa-engine.yaml"

    config_file.write_text(
        f"""
environments:
  development:
    base_url: "{local_api_server}"
    headless: true
    timeout: 5000
    api:
      headers:
        X-Client: "praman"
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PRAMAN_CONFIG_FILE", str(config_file))
    monkeypatch.setenv("PRAMAN_ENVIRONMENT", "development")

    api = request.getfixturevalue("praman_api")

    response = api.get("/health")

    assert response.status == 200
    assert response.json() == {
        "status": "ok",
        "service": "praman",
    }

    header_response = api.get("/headers")

    assert header_response.status == 200
    assert header_response.json() == {
        "x_client": "praman",
        "authorization": None,
    }


def test_api_fixture_rejects_incomplete_configuration(
    monkeypatch,
    request,
):
    monkeypatch.setenv("PRAMAN_CONFIG_FILE", ".\\qa-engine.yaml")
    monkeypatch.delenv("PRAMAN_ENVIRONMENT", raising=False)

    with pytest.raises(
        pytest.UsageError,
        match="Set both PRAMAN_CONFIG_FILE and PRAMAN_ENVIRONMENT",
    ):
        request.getfixturevalue("praman_api")


def test_api_session_disposes_context_when_session_exits(monkeypatch):
    mock_api_context = MagicMock()
    mock_playwright = MagicMock()
    mock_playwright.request.new_context.return_value = mock_api_context

    monkeypatch.setattr(
        "framework.api.session.sync_playwright",
        lambda: MagicMock(
            __enter__=MagicMock(return_value=mock_playwright),
            __exit__=MagicMock(return_value=False),
        ),
    )

    with pytest.raises(RuntimeError, match="simulated test failure"):
        with open_api_session("https://example.com") as api:
            assert api is mock_api_context
            raise RuntimeError("simulated test failure")

    mock_api_context.dispose.assert_called_once_with()


def test_pytest_fixture_provides_bearer_authentication(
    monkeypatch,
    tmp_path,
    local_api_server,
    request,
):
    config_file = tmp_path / "qa-engine.yaml"

    config_file.write_text(
        f"""
environments:
  development:
    base_url: "{local_api_server}"
    headless: true
    timeout: 5000
    api:
      authentication:
        type: bearer
        token_env: PRAMAN_API_TOKEN
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PRAMAN_CONFIG_FILE", str(config_file))
    monkeypatch.setenv("PRAMAN_ENVIRONMENT", "development")
    monkeypatch.setenv("PRAMAN_API_TOKEN", "test-praman-token")

    api = request.getfixturevalue("praman_api")

    response = api.get("/headers")

    assert response.status == 200
    assert response.json() == {
        "x_client": None,
        "authorization": "Bearer test-praman-token",
    }