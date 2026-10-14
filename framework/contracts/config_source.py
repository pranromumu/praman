from abc import ABC, abstractmethod
from typing import Dict, Any
from framework.contracts.normalized_provider import NormalizedConfigProvider

class ConfigSource(NormalizedConfigProvider):
    """
    The original Praman configuration source contract.
    """
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        pass