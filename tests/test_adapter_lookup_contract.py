import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.contracts.adapter_lookup import AdapterLookup
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter

# ==========================================
# Step 65: ABC Structural Contract Tests
# ==========================================

class MockAdapter:
    pass

class ValidLookup(AdapterLookup):
    def get_adapter(self, source_version: int, target_version: int):
        if source_version == 1 and target_version == 2:
            return MockAdapter
        return None

def test_1_adapter_lookup_is_abc():
    assert inspect.isabstract(AdapterLookup)

def test_2_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        AdapterLookup()

def test_3_valid_subclass_can_be_instantiated():
    lookup = ValidLookup()
    assert isinstance(lookup, AdapterLookup)

def test_4_lookup_returns_none_if_not_found():
    lookup = ValidLookup()
    assert lookup.get_adapter(9, 10) is None

def test_5_lookup_returns_class_if_found():
    lookup = ValidLookup()
    assert lookup.get_adapter(1, 2) is MockAdapter

def test_6_contract_is_minimal():
    public_methods = [m for m in dir(AdapterLookup) if not m.startswith('_')]
    assert "get_adapter" in public_methods
    assert "register_adapter" not in public_methods
    assert "finalize" not in public_methods

def test_7_no_concrete_imports_in_contract():
    source_code = inspect.getsource(AdapterLookup)
    assert "VersionedSource" not in source_code
    assert "environment" not in source_code
    assert "Normalization" not in source_code
    assert "CompatibilityRegistry" not in source_code


# ==========================================
# Step 71: Reusable Behavioral Contract Test
# ==========================================

class FakeAdapter:
    pass

class AnotherAdapter:
    pass

class FakeLookup(AdapterLookup):
    """A completely custom implementation that doesn't use a dict."""
    def __init__(self):
        self._mapping = {
            (1, 2): FakeAdapter,
            (3, 4): AnotherAdapter
        }
        
    def get_adapter(self, source_version: int, target_version: int):
        return self._mapping.get((source_version, target_version))

def assert_adapter_lookup_contract(lookup: AdapterLookup, known_transitions: list):
    """
    A reusable contract test for any AdapterLookup implementation.
    `known_transitions` is a list of tuples: (source, target, expected_adapter_class)
    """
    # 1 & 2: Verify known transitions return the exact expected callable class
    for source, target, expected_adapter in known_transitions:
        result = lookup.get_adapter(source, target)
        assert result is expected_adapter, \
            f"Lookup for ({source}, {target}) returned {result}, expected {expected_adapter}"
        assert callable(result), \
            f"Returned adapter for ({source}, {target}) is not callable"
            
    # 3: Verify an unknown transition returns None
    unknown_source = 9999
    unknown_target = 8888
    assert lookup.get_adapter(unknown_source, unknown_target) is None, \
        "Unknown transition should return None"

def test_8_fake_lookup_satisfies_contract():
    fake_lookup = FakeLookup()
    known = [
        (1, 2, FakeAdapter),
        (3, 4, AnotherAdapter)
    ]
    assert_adapter_lookup_contract(fake_lookup, known)

def test_9_compatibility_registry_satisfies_contract():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, V1ToV2Adapter)
    
    known = [
        (1, 2, V1ToV2Adapter)
    ]
    assert_adapter_lookup_contract(registry, known)