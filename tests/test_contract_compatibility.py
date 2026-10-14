import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.legacy_source import LegacySource
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.config.legacy_source_adapter import LegacySourceAdapter

def test_1_legacy_source_has_original_api():
    source = LegacySource()
    # Verify it has the old method
    assert hasattr(source, "get_config")
    # Verify it does NOT accept an environment argument
    sig = inspect.signature(source.get_config)
    assert "environment" not in sig.parameters
    assert len(sig.parameters) == 0  # Only 'self'

def test_2_adapter_implements_config_source_v2():
    assert issubclass(LegacySourceAdapter, ConfigSourceV2)
    
    legacy = LegacySource()
    adapter = LegacySourceAdapter(legacy)
    assert isinstance(adapter, ConfigSourceV2)

def test_3_adapter_accepts_environment():
    legacy = LegacySource()
    adapter = LegacySourceAdapter(legacy)
    
    # This should not raise a TypeError
    result = adapter.get_config("production")
    assert result is not None

def test_4_adapter_returns_legacy_configuration():
    legacy = LegacySource()
    adapter = LegacySourceAdapter(legacy)
    
    result = adapter.get_config("production")
    assert result == {"browser": "chromium"}

def test_5_legacy_source_was_not_modified():
    source_code = inspect.getsource(LegacySource)
    # Verify we didn't secretly add 'environment' to the LegacySource class
    assert "environment" not in source_code
    
    # Instantiate it to prove it still works exactly as before
    legacy = LegacySource()
    assert legacy.get_config() == {"browser": "chromium"}

def test_6_adapter_handles_multiple_environments():
    legacy = LegacySource()
    adapter = LegacySourceAdapter(legacy)
    
    # The adapter accepts all environments gracefully
    assert adapter.get_config("development") == {"browser": "chromium"}
    assert adapter.get_config("staging") == {"browser": "chromium"}
    assert adapter.get_config("production") == {"browser": "chromium"}