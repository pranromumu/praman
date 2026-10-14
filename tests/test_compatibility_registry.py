import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter

def test_1_register_adapter():
    registry = CompatibilityRegistry()
    registry.register_adapter(1, 2, V1ToV2Adapter)
    assert registry.get_adapter(1, 2) is V1ToV2Adapter

def test_2_get_adapter_returns_none_if_not_found():
    registry = CompatibilityRegistry()
    assert registry.get_adapter(1, 2) is None
    assert registry.get_adapter(2, 3) is None