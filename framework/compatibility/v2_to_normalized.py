from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.contracts.normalized_provider import NormalizedConfigProvider

class V2ToNormalizedProvider(NormalizedConfigProvider):
    """
    Binds a V2 source and an environment together, exposing a parameterless
    get_config() to the resolver.
    """
    
    def __init__(self, v2_source: ConfigSourceV2, environment: str):
        self._v2_source = v2_source
        self._environment = environment
        
    def get_config(self) -> dict:
        # The environment context is injected at construction, not at execution
        return self._v2_source.get_config(self._environment)