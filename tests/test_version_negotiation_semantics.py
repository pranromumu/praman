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

def test_1_mutually_supported_version_is_selected(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    result = negotiate_contract(vs, [2, 3], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)

def test_2_praman_highest_version_not_selected_if_client_unsupported(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1])
    # FIXED: Updated regex match string
    with pytest.raises(ValueError, match="No mutually supported contract version"):
        negotiate_contract(vs, [2, 3], registry, version_policy=HighestVersionPolicy())

def test_3_source_matches_target_returns_native(registry):
    source = NativeV2Source()
    vs = VersionedSource(source=source, source_version=2, supported_versions=[2])
    result = negotiate_contract(vs, [2, 3], registry, version_policy=HighestVersionPolicy())
    assert result is source

def test_4_no_mutual_version_fails(registry):
    vs = VersionedSource(source=NativeV2Source(), source_version=2, supported_versions=[2])
    # FIXED: Updated regex match string
    with pytest.raises(ValueError, match="No mutually supported contract version"):
        negotiate_contract(vs, [3], registry, version_policy=HighestVersionPolicy())

def test_5_mutual_version_exists_but_no_adapter_fails(registry):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    empty_registry = CompatibilityRegistry()
    with pytest.raises(ValueError, match="Adaptation failed: No adapter registered"):
        negotiate_contract(vs, [2], empty_registry, version_policy=HighestVersionPolicy())

def test_6_negotiation_has_no_hardcoded_branches():
    source_code = inspect.getsource(negotiate_contract)
    assert "== 1" not in source_code
    assert "== 2" not in source_code
    assert "isinstance" not in source_code
    assert "ConfigSourceV1" not in source_code