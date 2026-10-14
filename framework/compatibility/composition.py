from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.policies.version_policy_factory import VersionPolicyFactory
from framework.compatibility.policies.version_selection import HighestVersionPolicy, LowestVersionPolicy

def build_compatibility_registry() -> CompatibilityRegistry:
    """
    Composition root for the compatibility layer.
    Creates and populates the registry with known adapters.
    """
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, V1ToV2Adapter)
    registry.finalize()
    return registry

def build_version_policy_factory() -> VersionPolicyFactory:
    """
    Composition root for the version selection policies.
    Creates and populates the factory with known policies.
    """
    factory = VersionPolicyFactory()
    factory.register_policy("highest", HighestVersionPolicy)
    factory.register_policy("lowest", LowestVersionPolicy)
    return factory