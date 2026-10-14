import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source import ConfigSource
from framework.config.capabilities import Refreshable
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource, AnotherFakeSource, RefreshableFakeSource
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.environment import Environment

def test_1_minimal_contract():
    # Verify ConfigSource exposes get_config
    assert hasattr(ConfigSource, "get_config")
    
    # Verify it does NOT contain optional capabilities or infrastructure methods
    assert not hasattr(ConfigSource, "refresh")
    assert not hasattr(ConfigSource, "authenticate")
    assert not hasattr(ConfigSource, "validate")
    assert not hasattr(ConfigSource, "watch")

def test_2_existing_implementations_remain_valid():
    # All existing sources must still be valid subclasses of the stable contract
    assert issubclass(YAMLSource, ConfigSource)
    assert issubclass(EnvSource, ConfigSource)
    assert issubclass(CLISource, ConfigSource)
    assert issubclass(FakeConfigSource, ConfigSource)
    assert issubclass(AnotherFakeSource, ConfigSource)

def test_3_optional_capability_remains_separate():
    # RefreshableFakeSource implements both
    assert issubclass(RefreshableFakeSource, ConfigSource)
    assert issubclass(RefreshableFakeSource, Refreshable)
    
    # Ordinary sources do NOT implement the Refreshable capability
    assert not issubclass(YAMLSource, Refreshable)
    assert not issubclass(EnvSource, Refreshable)
    assert not issubclass(CLISource, Refreshable)
    assert not issubclass(FakeConfigSource, Refreshable)
    assert not issubclass(AnotherFakeSource, Refreshable)

def test_4_resolver_only_requires_stable_contract():
    # Create a brand new, minimal implementation inside the test
    class MinimalTestSource(ConfigSource):
        def get_config(self) -> dict:
            return {"browser": "chromium"}
            
    source = MinimalTestSource()
    spec = SourceSpec(source=source, failure_policy=FailurePolicy.REQUIRED)
    
    # The resolver should work perfectly with just this minimal implementation
    result = resolve_config([spec])
    assert result["browser"] == "chromium"

def test_5_contract_does_not_require_infrastructure_methods():
    # Inspect the source code of the ConfigSource contract
    source_code = inspect.getsource(ConfigSource)
    
    # Ensure no infrastructure or capability methods leaked into the contract definition
    assert "parse_yaml" not in source_code
    assert "authenticate" not in source_code
    assert "connect" not in source_code
    assert "refresh" not in source_code
    assert "validate" not in source_code