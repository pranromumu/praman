from abc import abstractmethod
from typing import Dict, Any
from framework.contracts.normalized_provider import NormalizedConfigProvider

class ConfigSourceV1(NormalizedConfigProvider):
    """
    The original Praman configuration source contract.
    Does not support environment selection.
    """
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        pass