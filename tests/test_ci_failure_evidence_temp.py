import os
import tempfile
from pathlib import Path


_test_root = Path(tempfile.gettempdir()) / "praman-ci-failure-evidence"
_test_root.mkdir(parents=True, exist_ok=True)

_config_path = _test_root / "qa-engine.yaml"
_config_path.write_text(
    "environments:\n"
    "  development:\n"
    "    base_url: 'http://127.0.0.1'\n"
    "    browser: 'chromium'\n"
    "    headless: true\n"
    "    timeout: 5000\n",
    encoding="utf-8",
)

os.environ["PRAMAN_CONFIG_FILE"] = str(_config_path)
os.environ["PRAMAN_ENVIRONMENT"] = "development"
os.environ["PRAMAN_REPORT_PATH"] = "artifacts/praman-report.json"
os.environ["PRAMAN_ARTIFACTS_DIR"] = "artifacts/failures"


def test_ci_failure_generates_evidence(praman_page):
    praman_page.set_content(
        "<html><head><title>Controlled Failure</title></head>"
        "<body><h1>PRAMAN CI Evidence Check</h1>"
        "<p>This failure is intentional.</p></body></html>"
    )
    assert praman_page.title() == "Expected Different Title"
