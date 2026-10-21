from framework.browser.session import open_browser_page
from framework.config.settings import Settings

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
    print("PASS: Chromium rendered local HTML and the title assertion succeeded.")
