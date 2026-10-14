import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.contracts.normalized_provider import NormalizedConfigProvider
from framework.compatibility.normalization import normalize_v2_source
from framework.compatibility.v2_to_normalized import V2ToNormalizedProvider

class NativeV2Source(ConfigSourceV2):
    def get_config(self, environment: str) -> dict:
        return {"browser": "webkit", "env": environment}

def test_1_returns_normalized_config_provider():
    source = NativeV2Source()
    result = normalize_v2_source(source, "production")
    assert isinstance(result, NormalizedConfigProvider)
    assert isinstance(result, V2ToNormalizedProvider)

def test_2_binds_environment_context():
    source = NativeV2Source()
    normalized = normalize_v2_source(source, "staging")
    
    # The normalized provider should have bound "staging"
    # Calling get_config() (no args) should internally call source.get_config("staging")
    config = normalized.get_config()
    assert config["env"] == "staging"
    assert config["browser"] == "webkit"

def test_3_does_not_perform_negotiation():
    # The function signature should not contain negotiation parameters
    sig = inspect.signature(normalize_v2_source)
    assert "source_version" not in sig.parameters
    assert "registry" not in sig.parameters
    assert "client_supported_versions" not in sig.parameters

def test_4_exposes_parameterless_get_config():
    source = NativeV2Source()
    normalized = normalize_v2_source(source, "production")
    sig = inspect.signature(normalized.get_config)
    # Should have no required arguments (other than self)
    assert len(sig.parameters) == 0