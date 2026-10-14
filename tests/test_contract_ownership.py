import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source import ConfigSource
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource, AnotherFakeSource
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.environment import Environment

def test_1_yaml_implements_config_source():
    assert issubclass(YAMLSource, ConfigSource)

def test_2_env_implements_config_source():
    assert issubclass(EnvSource, ConfigSource)

def test_3_cli_implements_config_source():
    assert issubclass(CLISource, ConfigSource)

def test_4_fake_implements_config_source():
    assert issubclass(FakeConfigSource, ConfigSource)

def test_5_another_fake_implements_config_source():
    assert issubclass(AnotherFakeSource, ConfigSource)

def test_6_resolver_imports_from_contracts():
    # Verify the resolver imports the contract from the new contracts location
    source_code = inspect.getsource(sys.modules['framework.config.resolver'])
    assert "from framework.contracts.config_source import ConfigSource" in source_code

def test_7_resolver_has_no_concrete_source_imports():
    source_code = inspect.getsource(sys.modules['framework.config.resolver'])
    
    # Resolver should not import concrete infrastructure
    assert "from framework.config.yaml_source" not in source_code
    assert "from framework.config.env_source" not in source_code
    assert "from framework.config.cli_source" not in source_code
    assert "from framework.config.fake_source" not in source_code

def test_8_replacing_implementation_does_not_change_resolver():
    # Implementation A (YAML-like via Fake)
    specs_a = [
        SourceSpec(source=FakeConfigSource({"browser": "firefox"}), failure_policy=FailurePolicy.REQUIRED)
    ]
    result_a = resolve_config(specs_a)
    assert result_a["browser"] == "firefox"
    
    # Implementation B (Completely different class)
    specs_b = [
        SourceSpec(source=AnotherFakeSource({"browser": "webkit"}), failure_policy=FailurePolicy.REQUIRED)
    ]
    result_b = resolve_config(specs_b)
    assert result_b["browser"] == "webkit"

def test_9_contract_contains_only_required_capability():
    # Verify the contract only defines get_config, no infrastructure leaks
    contract_methods = [method for method in dir(ConfigSource) if not method.startswith("_")]
    assert "get_config" in contract_methods
    # Ensure no infrastructure or lifecycle methods leaked into the contract
    assert "refresh" not in contract_methods
    assert "authenticate" not in contract_methods
    assert "parse_yaml" not in contract_methods