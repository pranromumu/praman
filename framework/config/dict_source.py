from typing import Any
from framework.config.source import ConfigSource

class DictSource(ConfigSource):
    """
    Configuration source backed by an existing dictionary.
    Useful for adapting already-parsed configuration data into the ConfigSource interface.
    """
    def __init__(self, config: dict[str, Any]):
        self._config = config

    def get_config(self) -> dict[str, Any]:
        # Return a copy to prevent mutation of the original dictionary
        return self._config.copy()