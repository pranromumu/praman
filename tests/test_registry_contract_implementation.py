import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.contracts.adapter_lookup import AdapterLookup

class FakeAdapter:
    def __init__(self, source):
        self.source = source

def test_1_compatibility_registry_is_adapter_lookup():
    registry = CompatibilityRegistry()
    assert isinstance(registry, AdapterLookup)

def test_2_get_adapter_behavior_still_works():
    registry = CompatibilityRegistry()
    # Returns None when not found
    assert registry.get_adapter(9, 10) is None
    
    # Returns class when found
    registry.register_adapter(1, 2, FakeAdapter)
    assert registry.get_adapter(1, 2) is FakeAdapter

def test_3_registration_behavior_still_works():
    registry = CompatibilityRegistry()
    # Duplicate fails
    registry.register_adapter(1, 2, FakeAdapter)
    with pytest.raises(ValueError, match="already registered"):
        registry.register_adapter(1, 2, FakeAdapter)
        
    # Same-version fails
    with pytest.raises(ValueError, match="cannot equal target_version"):
        registry.register_adapter(2, 2, FakeAdapter)
        
    # Non-callable fails
    with pytest.raises(ValueError, match="must be callable"):
        registry.register_adapter(1, 3, "not_callable")

def test_4_finalization_behavior_still_works():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    registry.finalize()
    
    # Lookup works
    assert registry.get_adapter(1, 2) is FakeAdapter
    
    # Registration blocked
    with pytest.raises(ValueError, match="finalized"):
        registry.register_adapter(3, 4, FakeAdapter)

def test_5_adapter_lookup_remains_minimal():
    # Verify the abstraction itself didn't accidentally inherit registry stuff
    public_methods = [m for m in dir(AdapterLookup) if not m.startswith('_')]
    assert "get_adapter" in public_methods
    assert "register_adapter" not in public_methods
    assert "finalize" not in public_methods