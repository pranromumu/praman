from abc import ABC, abstractmethod
from typing import Dict, Any

class NormalizedConfigProvider(ABC):
    """
    The stable core contract for the resolver.
    It guarantees that configuration can be fetched without requiring
    any application context (like environment) to be passed at execution time.
    """
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        pass