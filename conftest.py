import os

import pytest

from framework.browser.session import open_browser_page
from framework.config.environment import Environment
from framework.config.settings import Settings


@pytest.fixture
def praman_page():
    """Provide a browser page using explicit Praman configuration."""

    config_file = os.environ.get("PRAMAN_CONFIG_FILE")
    environment_name = os.environ.get("PRAMAN_ENVIRONMENT")

    if not config_file or not environment_name:
        raise pytest.UsageError(
            "Set both PRAMAN_CONFIG_FILE and PRAMAN_ENVIRONMENT "
            "to use the praman_page fixture."
        )

    settings = Settings.from_config_file(
        file_path=config_file,
        env=Environment.from_string(environment_name),
    )

    with open_browser_page(settings) as page:
        yield page
