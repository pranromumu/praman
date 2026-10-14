import inspect
from typing import Dict, Type
from framework.compatibility.policies.version_selection import VersionSelectionPolicy
from framework.compatibility.policies.policy_name_provider import PolicyNameProvider

class VersionPolicyFactory(PolicyNameProvider):
    """
    Factory for mapping string configuration names to VersionSelectionPolicy instances.
    Enforces strict fail-fast validation during registration.
    Implements the PolicyNameProvider contract for read-only name lookup.
    """
    def __init__(self):
        self._policies: Dict[str, Type[VersionSelectionPolicy]] = {}
        
    def register_policy(self, name: str, policy_class: Type[VersionSelectionPolicy]) -> None:
        """
        Registers a policy class for a given name.
        Raises ValueError if the registration is structurally invalid or a duplicate.
        """
        # 1. Validate name is a non-empty string
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Policy name must be a non-empty string.")
            
        # 2. Validate policy_class is a class/type
        if not isinstance(policy_class, type):
            raise ValueError(f"Policy class must be a type, but got {type(policy_class).__name__}.")
            
        # 3. Validate policy_class is a subclass of VersionSelectionPolicy
        if not issubclass(policy_class, VersionSelectionPolicy):
            raise ValueError(f"Policy class must be a subclass of VersionSelectionPolicy, got {policy_class.__name__}.")
            
        # 4. Validate policy_class is not abstract
        if inspect.isabstract(policy_class):
            raise ValueError(f"Cannot register abstract policy class: {policy_class.__name__}.")
            
        key = name.strip()
        
        # 5. Validate no duplicate registrations
        if key in self._policies:
            raise ValueError(f"Policy '{key}' is already registered. Cannot overwrite.")
            
        self._policies[key] = policy_class
        
    def create_policy(self, name: str) -> VersionSelectionPolicy:
        """
        Creates a new instance of the registered policy.
        Raises ValueError if the name is unknown.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Policy name must be a non-empty string.")
            
        key = name.strip()
        
        if key not in self._policies:
            raise ValueError(f"Unknown policy name: '{key}'. Supported policies: {list(self._policies.keys())}")
            
        policy_class = self._policies[key]
        # Return a new instance every time
        return policy_class()

    def get_supported_policy_names(self) -> list[str]:
        """
        Returns a list of registered policy names.
        Returns a new list to prevent external mutation of the factory's internal state.
        """
        return list(self._policies.keys())