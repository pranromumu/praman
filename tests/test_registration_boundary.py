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

class MockAdapter:
    def __init__(self, source):
        self.source = source

class FakeSource:
    pass

def test_1_builder_returns_registry():
    registry = build_compatibility_registry()
    assert isinstance(registry, CompatibilityRegistry)

def test_2_v1_to_v2_is_registered():
    registry = build_compatibility_registry()
    adapter = registry.get_adapter(1, 2)
    assert adapter is V1ToV2Adapter

def test_3_builder_owns_registration():
    source_code = inspect.getsource(build_compatibility_registry)
    assert "register_adapter" in source_code
    assert "V1ToV2Adapter" in source_code

def test_4_negotiation_does_not_register_adapters():
    source_code = inspect.getsource(negotiate_contract)
    assert "register_adapter" not in source_code
    assert "build_compatibility_registry" not in source_code
    assert "V1ToV2Adapter" not in source_code

def test_5_dependency_injection_with_mock_registry():
    custom_registry = CompatibilityRegistry()
    custom_registry.register_adapter(10, 20, MockAdapter)
    
    vs = VersionedSource(
        source=FakeSource(),
        source_version=10,
        supported_versions=[10, 20]
    )
    
    # FIXED: Added version_policy
    result = negotiate_contract(
        versioned_source=vs,
        praman_supported_versions=[20],
        registry=custom_registry,
        version_policy=HighestVersionPolicy()
    )
    
    assert isinstance(result, MockAdapter)