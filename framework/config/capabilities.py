from abc import ABC, abstractmethod

class Refreshable(ABC):
    """
    Capability interface for configuration sources that can be refreshed.
    Sources implementing this interface can update their internal state
    before configuration is read.
    """
    
    @abstractmethod
    def refresh(self) -> None:
        pass