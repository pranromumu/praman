import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.contracts.config_source import ConfigSource
from framework.config.fake_source import FakeConfigSource, AnotherFakeSource
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.resolver import resolve_config

def test_1_another_fake_source_implements_config_source():
    source = AnotherFakeSource({"browser": "firefox"})
    assert isinstance(source, ConfigSource)

def test_2_resolver_accepts_another_fake_source():
    source = AnotherFakeSource({"browser": "firefox"})
    spec = SourceSpec(source=source, failure_policy=FailurePolicy.REQUIRED)
    
    result = resolve_config([spec])
    assert result["browser"] == "firefox"

def test_3_resolver_accepts_multiple_implementations():
    fake1 = FakeConfigSource({"browser": "chromium"})
    fake2 = AnotherFakeSource({"browser": "firefox"})
    
    specs = [
        SourceSpec(source=fake1, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=fake2, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    result = resolve_config(specs)
    # fake2 (AnotherFakeSource) overrides fake1 (FakeConfigSource)
    assert result["browser"] == "firefox"

def test_4_resolver_contains_no_concrete_source_dependencies():
    source_code = inspect.getsource(resolve_config)
    
    # Verify the resolver source code never mentions concrete classes
    assert "FakeConfigSource" not in source_code
    assert "AnotherFakeSource" not in source_code
    assert "YAMLSource" not in source_code
    assert "EnvSource" not in source_code
    assert "CLISource" not in source_code

def test_5_dependency_is_injected_not_constructed():
    # Create two instances of AnotherFakeSource
    source_a = AnotherFakeSource({"base_url": "https://example.com", "browser": "firefox"})
    source_b = AnotherFakeSource({"browser": "chromium"})
    
    specs = [
        SourceSpec(source=source_a, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_b, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    # Resolver receives them via DI and merges them
    result = resolve_config(specs)
    assert result["base_url"] == "https://example.com"
    assert result["browser"] == "chromium"

def test_6_replacing_implementation_does_not_require_resolver_changes():
    # Implementation A
    specs_a = [
        SourceSpec(source=FakeConfigSource({"browser": "firefox"}), failure_policy=FailurePolicy.REQUIRED)
    ]
    result_a = resolve_config(specs_a)
    assert result_a["browser"] == "firefox"
    
    # Implementation B (using completely different class)
    specs_b = [
        SourceSpec(source=AnotherFakeSource({"browser": "webkit"}), failure_policy=FailurePolicy.REQUIRED)
    ]
    result_b = resolve_config(specs_b)
    assert result_b["browser"] == "webkit"
    
    # The exact same resolve_config function handled both without modification