from framework.contracts.config_source import ConfigSource
from framework.config.capabilities import Refreshable

class FakeConfigSource(ConfigSource):
    """
    A simple configuration source backed by an in-memory dictionary.
    """
    def __init__(self, config: dict):
        self._config = config

    def get_config(self) -> dict:
        return self._config

class RefreshableFakeSource(ConfigSource, Refreshable):
    """
    A fake source that implements both ConfigSource and the Refreshable capability.
    """
    def __init__(self, config: dict):
        self._config = config
        self.refresh_called = False
        
    def refresh(self) -> None:
        self.refresh_called = True
        
    def get_config(self) -> dict:
        return self._config

class AnotherFakeSource(ConfigSource):
    """
    A second independent fake configuration source.
    Used to prove the resolver depends on the abstraction, not concrete classes.
    """
    def __init__(self, config: dict):
        self._config = config

    def get_config(self) -> dict:
        return self._config