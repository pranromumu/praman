from abc import ABC, abstractmethod
from typing import List, Set

# The hardcoded SUPPORTED_POLICY_NAMES constant has been removed.
# The source of truth for supported policy names is now the VersionPolicyFactory,
# exposed via the PolicyNameProvider interface.

class VersionSelectionPolicy(ABC):
    """
    Abstract public contract for version selection policies.
    """
    @abstractmethod
    def select_version(
        self,
        client_supported_versions: List[int],
        praman_supported_versions: List[int]
    ) -> int:
        pass


class BaseVersionSelectionPolicy(VersionSelectionPolicy):
    """
    Intermediate base class that handles shared validation and intersection calculation.
    Uses the Template Method Pattern to delegate the final selection to concrete subclasses.
    """
    def select_version(
        self,
        client_supported_versions: List[int],
        praman_supported_versions: List[int]
    ) -> int:
        if not isinstance(client_supported_versions, list) or not client_supported_versions:
            raise ValueError("client_supported_versions must be a non-empty list.")
        if not isinstance(praman_supported_versions, list) or not praman_supported_versions:
            raise ValueError("praman_supported_versions must be a non-empty list.")

        for v in client_supported_versions:
            if not isinstance(v, int) or isinstance(v, bool):
                raise ValueError(f"Invalid version type in client_supported_versions: {v}. Must be an integer.")
        for v in praman_supported_versions:
            if not isinstance(v, int) or isinstance(v, bool):
                raise ValueError(f"Invalid version type in praman_supported_versions: {v}. Must be an integer.")

        mutual_versions = set(client_supported_versions) & set(praman_supported_versions)

        if not mutual_versions:
            raise ValueError("No mutually supported contract version.")

        return self.do_select_version(mutual_versions)

    @abstractmethod
    def do_select_version(self, mutual_versions: Set[int]) -> int:
        pass


class HighestVersionPolicy(BaseVersionSelectionPolicy):
    """Selects the highest mutually supported version."""
    def do_select_version(self, mutual_versions: Set[int]) -> int:
        return max(mutual_versions)


class LowestVersionPolicy(BaseVersionSelectionPolicy):
    """Selects the lowest mutually supported version."""
    def do_select_version(self, mutual_versions: Set[int]) -> int:
        return min(mutual_versions)