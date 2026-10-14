from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.contracts.normalized_provider import NormalizedConfigProvider
from framework.compatibility.v2_to_normalized import V2ToNormalizedProvider

def normalize_v2_source(
    source: ConfigSourceV2,
    environment: str
) -> NormalizedConfigProvider:
    """
    Binds environment context to a V2 source, returning a normalized provider.
    
    This function represents the architectural boundary between versioned contracts 
    (like ConfigSourceV2) and the stable, context-free contract (NormalizedConfigProvider) 
    expected by the core resolver.
    """
    return V2ToNormalizedProvider(source, environment)