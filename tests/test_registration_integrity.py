import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.compatibility.negotiation import negotiate_contract

class FakeAdapter:
    def __init__(self, source):
        self.source = source

def test_1_valid_registration_works():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    assert registry.get_adapter(1, 2) is FakeAdapter

def test_2_duplicate_registration_fails():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, FakeAdapter)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register_adapter(1, 2, FakeAdapter)

def test_3_same_version_fails():
    registry = CompatibilityRegistry()
    
    with pytest.raises(ValueError, match="cannot equal target_version"):
        registry.register_adapter(2, 2, FakeAdapter)

def test_4_none_adapter_fails():
    registry = CompatibilityRegistry()
    
    with pytest.raises(ValueError, match="Adapter must be callable"):
        registry.register_adapter(1, 2, None)

def test_5_non_callable_adapter_fails():
    registry = CompatibilityRegistry()
    
    with pytest.raises(ValueError, match="Adapter must be callable"):
        registry.register_adapter(1, 2, "not_an_adapter")

def test_6_negotiation_remains_unchanged():
    source_code = inspect.getsource(negotiate_contract)
    # Negotiation should not contain any of the registration validation logic
    assert "already registered" not in source_code
    assert "must be callable" not in source_code
    assert "cannot equal target_version" not in source_code