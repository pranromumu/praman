# framework/compatibility/contracts/adapter_lookup.py
from abc import ABC, abstractmethod
from typing import Optional, Type, Any

class AdapterLookup(ABC):
    """
    Minimal contract for looking up adapter classes based on version transitions.
    
    This abstraction is used by the runtime negotiation layer to find adapters.
    It intentionally excludes registration and lifecycle management to adhere
    to the Interface Segregation Principle (ISP).
    """

    @abstractmethod
    def get_adapter(self, source_version: int, target_version: int) -> Optional[Type[Any]]:
        """
        Retrieves the adapter class for a specific version transition.
        
        Args:
            source_version: The current contract version of the source.
            target_version: The target contract version.
            
        Returns:
            The adapter class if found, otherwise None.
        """
        pass