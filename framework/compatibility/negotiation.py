from typing import List
from framework.compatibility.contracts.adapter_lookup import AdapterLookup
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.compatibility.versioned_source import VersionedSource
from framework.compatibility.policies.version_selection import VersionSelectionPolicy

def negotiate_contract(
    versioned_source: VersionedSource,
    praman_supported_versions: List[int],
    registry: AdapterLookup,
    version_policy: VersionSelectionPolicy
) -> ConfigSourceV2:
    """
    Negotiates the contract version and adapts the source to the target version.
    
    Delegates version selection to the injected VersionSelectionPolicy.
    Delegates adapter lookup to the injected AdapterLookup.
    """
    client_source = versioned_source.source
    source_version = versioned_source.source_version
    client_supported_versions = versioned_source.supported_versions
    
    # 1. Delegate version selection to the policy.
    # The policy handles intersection, validation, and raising ValueError if no mutual version exists.
    target_version = version_policy.select_version(
        client_supported_versions,
        praman_supported_versions
    )
    
    # 2. If the source is already at the target version, return it natively
    if source_version == target_version:
        return client_source
        
    # 3. If versions mismatch, ask the registry for a direct adapter
    adapter_class = registry.get_adapter(source_version, target_version)
    
    if adapter_class:
        return adapter_class(client_source)
        
    # 4. If negotiation succeeded but adaptation failed, fail clearly
    raise ValueError(
        f"Adaptation failed: No adapter registered for conversion from version {source_version} to {target_version}."
    )