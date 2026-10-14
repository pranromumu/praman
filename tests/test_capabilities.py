import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source import ConfigSource
from framework.config.capabilities import Refreshable
from framework.config.fake_source import FakeConfigSource, RefreshableFakeSource
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy

def test_1_config_source_remains_unchanged():
    # Verify ConfigSource still only requires get_config
    assert hasattr(ConfigSource, "get_config")
    assert not hasattr(ConfigSource, "refresh")

def test_2_unrelated_sources_do_not_contaminate():
    # YAML, ENV, and CLI sources should NOT be Refreshable
    assert not issubclass(YAMLSource, Refreshable)
    assert not issubclass(EnvSource, Refreshable)
    assert not issubclass(CLISource, Refreshable)
    
    # The standard FakeConfigSource should not be Refreshable either
    assert not issubclass(FakeConfigSource, Refreshable)

def test_3_source_can_gain_optional_capability():
    # RefreshableFakeSource implements BOTH interfaces
    assert issubclass(RefreshableFakeSource, ConfigSource)
    assert issubclass(RefreshableFakeSource, Refreshable)

def test_4_resolver_remains_unchanged():
    # Verify the resolver source code doesn't know about Refreshable or refresh()
    source_code = inspect.getsource(resolve_config)
    assert "Refreshable" not in source_code
    assert "refresh()" not in source_code

def test_5_resolver_processes_refreshable_source_without_calling_refresh():
    # The resolver should just call get_config(), ignoring the refresh capability
    source = RefreshableFakeSource({"browser": "firefox"})
    spec = SourceSpec(source=source, failure_policy=FailurePolicy.REQUIRED)
    
    result = resolve_config([spec])
    
    assert result["browser"] == "firefox"
    # The resolver should NOT have called refresh()
    assert source.refresh_called is False

def test_6_composition_layer_can_handle_capability():
    # Prove that the composition layer *could* call refresh if it wanted to
    source = RefreshableFakeSource({"browser": "firefox"})
    
    # The composition layer checks for the capability and uses it
    if isinstance(source, Refreshable):
        source.refresh()
        
    assert source.refresh_called is True