import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_selection import HighestVersionPolicy
from framework.compatibility.composition import build_compatibility_registry
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.versioned_source import VersionedSource
from framework.config.legacy_v1_source import LegacyV1Source

class FakeAdapter:
    def __init__(self, source):
        self.source = source

def test_1_builder_returns_finalized_registry():
    registry = build_compatibility_registry()
    assert registry._finalized is True

def test_2_v1_to_v2_is_still_registered():
    registry = build_compatibility_registry()
    assert registry.get_adapter(1, 2) is V1ToV2Adapter

def test_3_returned_registry_rejects_new_registrations():
    registry = build_compatibility_registry()
    with pytest.raises(ValueError, match="Cannot register adapters after registry has been finalized"):
        registry.register_adapter(10, 20, FakeAdapter)

def test_4_negotiation_still_works_with_builder_registry():
    registry = build_compatibility_registry()
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    
    # FIXED: Added version_policy
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_5_builder_calls_finalize():
    source_code = inspect.getsource(build_compatibility_registry)
    assert "finalize()" in source_code

def test_6_registration_happens_before_finalization():
    source_code = inspect.getsource(build_compatibility_registry)
    register_pos = source_code.find("register_adapter")
    finalize_pos = source_code.find("finalize()")
    
    assert register_pos != -1
    assert finalize_pos != -1
    assert register_pos < finalize_pos