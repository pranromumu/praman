import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source_v1 import ConfigSourceV1
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.config.legacy_v1_source import LegacyV1Source
from framework.compatibility.v1_to_v2 import V1ToV2Adapter

def test_1_v1_contract():
    source = LegacyV1Source()
    assert isinstance(source, ConfigSourceV1)

def test_2_v2_contract():
    legacy = LegacyV1Source()
    adapter = V1ToV2Adapter(legacy)
    assert isinstance(adapter, ConfigSourceV2)

def test_3_translation():
    legacy = LegacyV1Source()
    adapter = V1ToV2Adapter(legacy)
    
    result = adapter.get_config("production")
    assert result == {"browser": "chromium"}

def test_4_v1_remains_unchanged():
    source = LegacyV1Source()
    # Verify it still works exactly as before without environment arguments
    result = source.get_config()
    assert result == {"browser": "chromium"}

def test_5_multiple_environments():
    legacy = LegacyV1Source()
    adapter = V1ToV2Adapter(legacy)
    
    # The adapter accepts all environments gracefully
    assert adapter.get_config("development") == {"browser": "chromium"}
    assert adapter.get_config("staging") == {"browser": "chromium"}
    assert adapter.get_config("production") == {"browser": "chromium"}

def test_6_normalized_contract():
    # This represents the Praman V2 core consumer
    def consume_v2_source(source: ConfigSourceV2) -> dict:
        return source.get_config("production")
        
    legacy = LegacyV1Source()
    adapter = V1ToV2Adapter(legacy)
    
    # The core consumer only knows about V2 and works perfectly with the adapter
    result = consume_v2_source(adapter)
    assert result == {"browser": "chromium"}