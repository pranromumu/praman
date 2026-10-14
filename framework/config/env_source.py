import os

from framework.contracts.config_source import ConfigSource


class EnvSource(ConfigSource):
    """
    Configuration source that reads PRAMAN_* environment variables.

    Responsible for:
    - Reading environment variables
    - Converting raw strings into appropriate Python types

    Not responsible for:
    - Configuration precedence
    - Business validation
    - Browser support validation
    """

    def __init__(self, environ=None):
        self.environ = environ if environ is not None else os.environ

    def get_config(self) -> dict:
        overrides = {}

        base_url = self.environ.get("PRAMAN_BASE_URL")
        if base_url is not None:
            overrides["base_url"] = base_url

        browser = self.environ.get("PRAMAN_BROWSER")
        if browser is not None:
            overrides["browser"] = browser

        headless = self.environ.get("PRAMAN_HEADLESS")
        if headless is not None:
            value = headless.lower()

            if value == "true":
                overrides["headless"] = True
            elif value == "false":
                overrides["headless"] = False
            else:
                raise ValueError(
                    f"Invalid value for PRAMAN_HEADLESS: '{headless}'. "
                    f"Expected 'true' or 'false' (case-insensitive)."
                )

               # ... existing code ...
        timeout = self.environ.get("PRAMAN_TIMEOUT")
        if timeout is not None:
            try:
                overrides["timeout"] = int(timeout)
            except ValueError:
                raise ValueError(
                    f"Invalid value for PRAMAN_TIMEOUT: '{timeout}'. "
                    f"Expected an integer."
                )

        # NEW: Version Policy override
        version_policy = self.environ.get("PRAMAN_VERSION_POLICY")
        if version_policy is not None:
            overrides["version_policy"] = version_policy

        return overrides