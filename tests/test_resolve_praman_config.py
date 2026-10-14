import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.composition import resolve_praman_config
from framework.compatibility.composition import build_compatibility_registry, build_version_policy_factory
from framework.compatibility.registry import CompatibilityRegistry
from framework.config.legacy_v1_source import LegacyV1Source
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.config.resolver import resolve_config
from framework.config.failure_policy import FailurePolicy
from framework.compatibility.versioned_source import VersionedSource

class NativeV2Source(ConfigSourceV2):
    def get_config(self, environment: str = None) -> dict:
        return {"browser": "webkit", "env": environment, "headless": True}

@pytest.fixture
def registry():
    return build_compatibility_registry()

@pytest.fixture
def factory():
    return build_version_policy_factory()

def test_1_v1_to_v2_pipeline_resolution(registry, factory):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    # FIXED: Added factory and version_policy_name
    result = resolve_praman_config(
        versioned_source=vs,
        praman_supported_versions=[2],
        environment="production",
        registry=registry,
        policy_factory=factory,
        version_policy_name="highest"
    )
    assert result["browser"] == "chromium"

def test_2_native_v2_pipeline_resolution(registry, factory):
    vs = VersionedSource(source=NativeV2Source(), source_version=2, supported_versions=[2])
    # FIXED: Added factory and version_policy_name
    result = resolve_praman_config(
        versioned_source=vs,
        praman_supported_versions=[2],
        environment="staging",
        registry=registry,
        policy_factory=factory,
        version_policy_name="highest"
    )
    assert result["browser"] == "webkit"
    assert result["env"] == "staging"

def test_3_registry_is_injected(monkeypatch, registry, factory):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1])
    
    called_with_registry = {"yes": False}
    def mock_negotiate(*args, **kwargs):
        called_with_registry["yes"] = kwargs.get("registry") is registry
        return NativeV2Source() 
        
    monkeypatch.setattr("framework.config.composition.negotiate_contract", mock_negotiate)
    
    # FIXED: Added factory and version_policy_name
    resolve_praman_config(
        versioned_source=vs,
        praman_supported_versions=[1],
        environment="dev",
        registry=registry,
        policy_factory=factory,
        version_policy_name="highest"
    )
    
    assert called_with_registry["yes"] is True

def test_4_resolver_remains_unaware_of_compatibility():
    source_code = inspect.getsource(resolve_config)
    assert "negotiate_contract" not in source_code
    assert "normalize_v2_source" not in source_code
    assert "resolve_praman_config" not in source_code
    assert "ConfigSourceV2" not in source_code

def test_5_no_compatibility_logic_duplicated_in_composition_root():
    source_code = inspect.getsource(resolve_praman_config)
    assert "negotiate_contract(" in source_code
    assert "normalize_v2_source(" in source_code
    assert "resolve_config(" in source_code
    assert "isinstance" not in source_code
    assert "if source_version ==" not in source_code
    assert "ConfigSourceV1" not in source_code