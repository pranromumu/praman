from abc import ABC, abstractmethod
from typing import Dict, Any

class ConfigSource(ABC):
    """
    Abstract base class defining the contract for configuration providers.
    
    A configuration source is responsible for acquiring configuration data
    from a specific origin (e.g., YAML file, environment variables, CLI arguments)
    and returning it as a dictionary with correctly typed Python values.
    
    The ConfigResolver relies on this contract and does not need to know
    the specific implementation details of how the data was fetched.
    """
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Fetches and returns the configuration data as a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary containing the configuration key-value pairs.
                           Returns an empty dict if no configuration is provided by this source.
        """
        pass