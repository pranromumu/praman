import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_selection import HighestVersionPolicy
from framework.compatibility.composition import build_compatibility_registry
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.normalization import normalize_v2_source
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.versioned_source import VersionedSource
from framework.config.legacy_v1_source import LegacyV1Source
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.contracts.normalized_provider import NormalizedConfigProvider
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy

class NativeV2Source(ConfigSourceV2):
    def get_config(self, environment: str = None) -> dict:
        return {"browser": "webkit", "env": environment}

def test_1_composition_root_creates_and_populates_registry():
    registry = build_compatibility_registry()
    assert isinstance(registry, CompatibilityRegistry)
    assert registry.get_adapter(1, 2) is V1ToV2Adapter

def test_2_negotiation_uses_injected_registry():
    registry = build_compatibility_registry()
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # FIXED: Added space and version_policy
    result = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    assert isinstance(result, V1ToV2Adapter)
    assert isinstance(result, ConfigSourceV2)

def test_3_negotiation_does_not_construct_registry():
    source_code = inspect.getsource(negotiate_contract)
    assert "CompatibilityRegistry()" not in source_code
    assert "register_adapter" not in source_code

def test_4_resolver_remains_completely_unaware():
    source_code = inspect.getsource(resolve_config)
    assert "CompatibilityRegistry" not in source_code
    assert "negotiate_contract" not in source_code
    assert "V1ToV2Adapter" not in source_code
    assert "normalize_v2_source" not in source_code

def test_5_full_pipeline_works_with_composition():
    registry = build_compatibility_registry()
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # FIXED: Added version_policy here
    adapted_v2 = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    normalized = normalize_v2_source(adapted_v2, "production")
    assert isinstance(normalized, NormalizedConfigProvider)
    specs = [SourceSpec(source=normalized, failure_policy=FailurePolicy.REQUIRED)]
    result = resolve_config(specs)
    assert result["browser"] == "chromium"

def test_6_native_v2_source_works_through_pipeline():
    registry = build_compatibility_registry()
    native = NativeV2Source()
    vs = VersionedSource(source=native, source_version=2, supported_versions=[2])
    # FIXED: Added space and version_policy
    result_v2 = negotiate_contract(vs, [2], registry, version_policy=HighestVersionPolicy())
    normalized = normalize_v2_source(result_v2, "staging")
    assert isinstance(normalized, NormalizedConfigProvider)
    assert normalized._v2_source is native
    specs = [SourceSpec(source=normalized, failure_policy=FailurePolicy.REQUIRED)]
    result = resolve_config(specs)
    assert result["browser"] == "webkit"
    assert result["env"] == "staging"

def test_7_normalization_does_not_perform_negotiation():
    source_code = inspect.getsource(normalize_v2_source)
    assert "negotiate_contract" not in source_code
    assert "source_version" not in source_code
    assert "registry" not in source_code