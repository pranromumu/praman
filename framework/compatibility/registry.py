from typing import Dict, Tuple, Type, Optional, Any
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.compatibility.contracts.adapter_lookup import AdapterLookup

class CompatibilityRegistry(AdapterLookup):
    """
    Registry for mapping contract version transitions to their adapter classes.
    Enforces strict fail-fast validation during registration and immutability after finalization.
    Implements the AdapterLookup contract for runtime consumption.
    """
    def __init__(self):
        self._adapters: Dict[Tuple[int, int], Type[ConfigSourceV2]] = {}
        self._finalized: bool = False
        
    def register_adapter(self, source_version: int, target_version: int, adapter_class: Any) -> None:
        """
        Registers an adapter class for a specific version transition.
        Raises ValueError if the registry is finalized or the registration is structurally invalid.
        """
        # Lifecycle enforcement
        if self._finalized:
            raise ValueError("Cannot register adapters after registry has been finalized.")
            
        # 1. Validate versions are integers
        if not isinstance(source_version, int) or not isinstance(target_version, int):
            raise ValueError("source_version and target_version must be integers.")
            
        # 2. Validate source != target (same-version adaptation is logically unnecessary)
        if source_version == target_version:
            raise ValueError(f"source_version ({source_version}) cannot equal target_version ({target_version}). No adaptation should be needed.")
            
        # 3. Validate adapter is usable/callable
        if adapter_class is None or not callable(adapter_class):
            raise ValueError(f"Adapter must be callable, but got {adapter_class}.")
            
        key = (source_version, target_version)
        
        # 4. Validate no duplicate registrations
        if key in self._adapters:
            raise ValueError(f"Adapter for transition {key} is already registered. Cannot overwrite.")
            
        self._adapters[key] = adapter_class
        
    def get_adapter(self, source_version: int, target_version: int) -> Optional[Type[ConfigSourceV2]]:
        """Retrieves the adapter class for a specific version transition."""
        return self._adapters.get((source_version, target_version))
        
    def finalize(self) -> None:
        """
        Locks the registry, preventing further registrations.
        This operation is idempotent: calling it multiple times is safe and does nothing.
        """
        self._finalized = True