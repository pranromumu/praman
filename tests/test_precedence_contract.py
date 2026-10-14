import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.fake_source import FakeConfigSource
from framework.config.source import ConfigSource
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.resolver import resolve_config

# Helper for Test 5: A source that always fails
class FailingSource(ConfigSource):
    def get_config(self):
        raise RuntimeError("Source unavailable")

# ─── Step 20: Precedence Contract Tests ──────────────────────────────────

def test_1_later_source_wins():
    source_a = FakeConfigSource({"browser": "chromium"})
    source_b = FakeConfigSource({"browser": "firefox"})
    source_c = FakeConfigSource({"browser": "webkit"})
    
    specs = [
        SourceSpec(source=source_a, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_b, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_c, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    result = resolve_config(specs)
    assert result["browser"] == "webkit"

def test_2_reordering_changes_result():
    source_a = FakeConfigSource({"browser": "chromium"})
    source_b = FakeConfigSource({"browser": "firefox"})
    source_c = FakeConfigSource({"browser": "webkit"})
    
    # Reorder to C -> A -> B
    specs = [
        SourceSpec(source=source_c, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_a, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_b, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    result = resolve_config(specs)
    # B is now last, so B should win
    assert result["browser"] == "firefox"

def test_3_resolver_does_not_sort():
    # Simulate a logically reversed order: CLI-like -> YAML-like -> ENV-like
    # The resolver should NOT know these names mean anything.
    cli_like = FakeConfigSource({"browser": "webkit"})
    yaml_like = FakeConfigSource({"browser": "chromium"})
    env_like = FakeConfigSource({"browser": "firefox"})
    
    specs = [
        SourceSpec(source=cli_like, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=yaml_like, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env_like, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    result = resolve_config(specs)
    # env_like is last, so it wins. Resolver didn't try to "fix" it by putting CLI last.
    assert result["browser"] == "firefox"

def test_4_partial_dictionaries():
    source_a = FakeConfigSource({"browser": "chromium", "timeout": 30000})
    source_b = FakeConfigSource({"browser": "firefox"})
    source_c = FakeConfigSource({"headless": False})
    
    specs = [
        SourceSpec(source=source_a, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_b, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=source_c, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    result = resolve_config(specs)
    assert result == {
        "browser": "firefox",
        "timeout": 30000,
        "headless": False
    }

def test_5_failure_policy_remains_independent(caplog):
    valid_yaml = FakeConfigSource({"browser": "chromium", "timeout": 30000})
    failing_env = FailingSource()
    valid_cli = FakeConfigSource({"browser": "webkit"})
    
    specs = [
        SourceSpec(source=valid_yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=failing_env, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=valid_cli, failure_policy=FailurePolicy.REQUIRED)
    ]
    
    with caplog.at_level("WARNING"):
        result = resolve_config(specs)
        
    # The optional failure didn't stop the pipeline, and CLI still overrode YAML
    assert result["browser"] == "webkit"
    assert result["timeout"] == 30000
    assert "Optional configuration source" in caplog.text