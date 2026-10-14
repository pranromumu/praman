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

class FakeLookup(CompatibilityRegistry):
    def get_adapter(self, source_version: int, target_version: int):
        if (source_version, target_version) == (10, 20):
            return FakeAdapter
        return None

class FakeSource:
    pass

def test_1_negotiation_works_with_concrete_registry():
    registry = build_compatibility_registry()
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # FIXED: Added version_policy
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_2_negotiation_works_with_fake_lookup():
    fake_registry = FakeLookup()
    vs = VersionedSource(source=FakeSource(), source_version=10, supported_versions=[10, 20])
    # FIXED: Added version_policy
    result = negotiate_contract(vs, [20], fake_registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, FakeAdapter)

def test_3_negotiation_does_not_import_compatibility_registry():
    source_code = inspect.getsource(negotiate_contract)
    assert "CompatibilityRegistry" not in source_code

def test_4_negotiation_does_not_call_register_adapter():
    source_code = inspect.getsource(negotiate_contract)
    assert "register_adapter" not in source_code

def test_5_negotiation_does_not_call_finalize():
    source_code = inspect.getsource(negotiate_contract)
    assert "finalize" not in source_code

def test_6_existing_behavior_unchanged():
    registry = build_compatibility_registry()
    vs_ok = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # FIXED: Added version_policy
    result = negotiate_contract(vs_ok, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)
    
    vs_fail = VersionedSource(source=FakeSource(), source_version=99, supported_versions=[99])
    with pytest.raises(ValueError, match="No mutually supported"):
        negotiate_contract(vs_fail, [100], registry, version_policy=HighestVersionPolicy())