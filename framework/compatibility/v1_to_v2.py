from framework.contracts.config_source_v1 import ConfigSourceV1
from framework.contracts.config_source_v2 import ConfigSourceV2

class V1ToV2Adapter(ConfigSourceV2):
    """
    Adapter that allows a V1 ConfigSource to be used where a ConfigSourceV2 is expected.
    """
    
    def __init__(self, v1_source: ConfigSourceV1):
        self._v1_source = v1_source
        
    def get_config(self, environment: str) -> dict:
        # The V1 source doesn't understand environments, so we ignore it 
        # and call the original method.
        return self._v1_source.get_config()