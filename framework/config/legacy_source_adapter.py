from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.config.legacy_source import LegacySource
from typing import Dict, Any

class LegacySourceAdapter(ConfigSourceV2):
    """
    Adapter that allows a LegacySource to be used where a ConfigSourceV2 is expected.
    """
    
    def __init__(self, legacy_source: LegacySource):
        self._legacy_source = legacy_source
        
    def get_config(self, environment: str) -> Dict[str, Any]:
        # The legacy source doesn't support environments, so we call its original method.
        # In a real system, we might log a warning that the environment argument was ignored.
        return self._legacy_source.get_config()