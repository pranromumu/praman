import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_selection import HighestVersionPolicy
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.versioned_source import VersionedSource
from framework.config.legacy_v1_source import LegacyV1Source

class NativeV2Source(ConfigSourceV2):
    def get_config(self, environment: str = None) -> dict:
        return {"browser": "webkit", "env": environment}

class FakeAdapter:
    def __init__(self, source):
        self.source = source
    def get_config(self, environment: str) -> dict:
        return {"adapted": True}

@pytest.fixture
def registry():
    reg = CompatibilityRegistry()
    reg.register_adapter(1, 2, V1ToV2Adapter)
    return reg

def test_1_same_version_returns_source(registry):
    source = NativeV2Source()
    vs = VersionedSource(source=source, source_version=2, supported_versions=[2])
    # ADDED version_policy HERE
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert result is source

def test_2_direct_adapter_is_loaded_from_registry(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # ADDED version_policy HERE
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)
    assert isinstance(result, ConfigSourceV2)

def test_3_missing_adapter_fails(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 3])
    with pytest.raises(ValueError, match="Adaptation failed: No adapter registered"):
        # ADDED version_policy HERE
        negotiate_contract(vs, [3], registry, version_policy=HighestVersionPolicy())

def test_4_fake_registered_adapter_works(registry):
    registry.register_adapter(10, 20, FakeAdapter)
    class FakeSource: pass
    vs = VersionedSource(source=FakeSource(), source_version=10, supported_versions=[10, 20])
    # ADDED version_policy HERE
    result = negotiate_contract(vs, [20], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, FakeAdapter)

def test_5_negotiation_has_no_concrete_adapter_reference():
    source_code = inspect.getsource(negotiate_contract)
    assert "V1ToV2Adapter" not in source_code

def test_6_negotiation_has_no_concrete_source_reference():
    source_code = inspect.getsource(negotiate_contract)
    assert "ConfigSourceV1" not in source_code
    # V2 is allowed as return type
    assert "LegacyV1Source" not in source_code
    assert "isinstance" not in source_code