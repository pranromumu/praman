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

@pytest.fixture
def registry():
    reg = CompatibilityRegistry()
    reg.register_adapter(1, 2, V1ToV2Adapter)
    return reg

def test_1_finds_mutually_supported_version(registry):
    vs = VersionedSource(source=NativeV2Source(), source_version=2, supported_versions=[2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, NativeV2Source)

def test_2_direct_adapter_is_loaded_from_registry(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)
    assert isinstance(result, ConfigSourceV2)

def test_3_highest_mutually_supported_wins_if_no_preference(registry):
    vs = VersionedSource(source=NativeV2Source(), source_version=2, supported_versions=[2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, NativeV2Source)

def test_4_no_common_version_without_adapter_fails(registry):
    vs = VersionedSource(source=NativeV2Source(), source_version=3, supported_versions=[3])
    # FIXED: Updated regex match string to match the new policy error message
    with pytest.raises(ValueError, match="No mutually supported contract version"):
        negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())

def test_5_no_common_version_with_adapter_succeeds(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_6_adapter_applied_when_v1_is_selected(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_7_resulting_object_is_always_v2(registry):
    vs1 = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result1 = negotiate_contract(vs1, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result1, ConfigSourceV2)
    
    vs2 = VersionedSource(source=NativeV2Source(), source_version=2, supported_versions=[2])
    result2 = negotiate_contract(vs2, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result2, ConfigSourceV2)

def test_8_core_consumer_does_not_contain_branching():
    from framework.config.resolver import resolve_config
    resolver_code = inspect.getsource(resolve_config)
    assert "ConfigSourceV1" not in resolver_code
    assert "ConfigSourceV2" not in resolver_code
    assert "isinstance" not in resolver_code