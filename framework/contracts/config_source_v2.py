from abc import ABC, abstractmethod
from typing import Dict, Any

class ConfigSourceV2(ABC):
    """
    The new Praman v2 configuration source contract.
    Requires environment selection.
    """
    
    @abstractmethod
    def get_config(self, environment: str) -> Dict[str, Any]:
        pass