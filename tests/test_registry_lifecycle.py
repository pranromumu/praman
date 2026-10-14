import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_selection import HighestVersionPolicy # FIXED: Added missing import
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.versioned_source import VersionedSource
from framework.config.legacy_v1_source import LegacyV1Source

class FakeAdapter:
    def __init__(self, source):
        self.source = source

def test_1_registry_starts_mutable():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    assert registry.get_adapter(1, 2) is FakeAdapter

def test_2_registration_works_before_finalization():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    assert registry.get_adapter(1, 2) is FakeAdapter

def test_3_finalize_changes_lifecycle_state():
    registry = CompatibilityRegistry()
    assert registry._finalized is False
    registry.finalize()
    assert registry._finalized is True

def test_4_registration_after_finalization_fails():
    registry = CompatibilityRegistry()
    registry.finalize()
    with pytest.raises(ValueError, match="Cannot register adapters after registry has been finalized"):
        registry.register_adapter(1, 2, FakeAdapter)

def test_5_lookup_still_works_after_finalization():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    registry.finalize()
    assert registry.get_adapter(1, 2) is FakeAdapter

def test_6_finalization_is_idempotent():
    registry = CompatibilityRegistry()
    registry.finalize()
    registry.finalize()
    assert registry._finalized is True

def test_7_negotiate_contract_works_with_finalized_registry():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, V1ToV2Adapter)
    registry.finalize()
    
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_8_existing_duplicate_registration_protection_still_works():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register_adapter(1, 2, FakeAdapter)