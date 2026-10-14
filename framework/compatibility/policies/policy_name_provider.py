from abc import ABC, abstractmethod

class PolicyNameProvider(ABC):
    """Contract for discovering supported policy names."""
    @abstractmethod
    def get_supported_policy_names(self) -> list[str]:
        """Return the currently supported policy names."""
        pass