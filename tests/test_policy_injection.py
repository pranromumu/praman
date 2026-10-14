import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.versioned_source import VersionedSource
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.config.legacy_v1_source import LegacyV1Source
from framework.compatibility.policies.version_selection import HighestVersionPolicy, LowestVersionPolicy

@pytest.fixture
def registry():
    reg = CompatibilityRegistry()
    reg.register_adapter(1, 2, V1ToV2Adapter)
    return reg

def test_lowest_version_policy_changes_target_without_changing_negotiation(registry):
    # Client supports [1, 2, 3]. Praman supports [2, 3, 4]. Source is V1.
    # Intersection is {2, 3}.
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2, 3])
    
    # 1. With HighestVersionPolicy -> selects 3 -> negotiation looks for (1, 3) -> fails adaptation
    with pytest.raises(ValueError, match="Adaptation failed: No adapter registered for conversion from version 1 to 3"):
        negotiate_contract(vs, [2, 3, 4], registry, version_policy=HighestVersionPolicy())
        
    # 2. With LowestVersionPolicy -> selects 2 -> negotiation looks for (1, 2) -> succeeds
    result = negotiate_contract(vs, [2, 3, 4], registry, version_policy=LowestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)