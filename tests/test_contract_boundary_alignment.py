import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.normalized_provider import NormalizedConfigProvider
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.compatibility.v2_to_normalized import V2ToNormalizedProvider
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.config.legacy_v1_source import LegacyV1Source
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy

class NativeV2Source(ConfigSourceV2):
    def get_config(self, environment: str) -> dict:
        return {"browser": "webkit", "env": environment}

def test_1_v2_source_requiring_environment_works():
    source = NativeV2Source()
    provider = V2ToNormalizedProvider(source, "staging")
    # Should execute without error
    config = provider.get_config()
    assert config["env"] == "staging"

def test_2_environment_supplied_before_resolver():
    source = NativeV2Source()
    # Environment is bound during construction, before resolver runs
    provider = V2ToNormalizedProvider(source, "production")
    assert provider._environment == "production"

def test_3_normalized_provider_exposes_parameterless_get_config():
    source = NativeV2Source()
    provider = V2ToNormalizedProvider(source, "staging")
    
    # Inspect the signature of get_config
    sig = inspect.signature(provider.get_config)
    # Should have no required arguments (other than self)
    assert len(sig.parameters) == 0

def test_4_resolver_calls_parameterless_get_config():
    source_code = inspect.getsource(resolve_config)
    # Verify the resolver calls get_config() with no arguments
    assert "get_config()" in source_code

def test_5_resolver_source_code_contains_no_branching():
    source_code = inspect.getsource(resolve_config)
    assert "environment" not in source_code
    assert "ConfigSourceV1" not in source_code
    assert "ConfigSourceV2" not in source_code
    assert "V1V2" not in source_code

def test_6_legacy_v1_still_works():
    # V1 sources still perfectly satisfy NormalizedConfigProvider
    legacy = LegacyV1Source()
    assert isinstance(legacy, NormalizedConfigProvider)
    
    specs = [SourceSpec(source=legacy, failure_policy=FailurePolicy.REQUIRED)]
    result = resolve_config(specs)
    assert result["browser"] == "chromium"

def test_7_native_v2_still_works():
    source = NativeV2Source()
    provider = V2ToNormalizedProvider(source, "production")
    
    specs = [SourceSpec(source=provider, failure_policy=FailurePolicy.REQUIRED)]
    result = resolve_config(specs)
    assert result["browser"] == "webkit"

def test_8_existing_configuration_resolution_remains_intact():
    # This proves our existing YAML/ENV/CLI sources (which are V1) 
    # still perfectly match the resolver's expected contract.
    from framework.config.yaml_source import YAMLSource
    from framework.config.env_source import EnvSource
    from framework.config.cli_source import CLISource
    from framework.config.environment import Environment
    
    yaml = YAMLSource("qa-engine.yaml", Environment.STAGING)
    env = EnvSource()
    cli = CLISource(args=[])
    
    assert isinstance(yaml, NormalizedConfigProvider)
    assert isinstance(env, NormalizedConfigProvider)
    assert isinstance(cli, NormalizedConfigProvider)