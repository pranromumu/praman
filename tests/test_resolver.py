import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.source import ConfigSource
from framework.config.resolver import resolve_config
from framework.config.failure_policy import FailurePolicy
from framework.config.source_spec import SourceSpec

class FakeConfigSource(ConfigSource):
    def __init__(self, config):
        self._config = config
    def get_config(self):
        return self._config

class LowPrioritySource(ConfigSource):
    def get_config(self):
        return {"browser": "chromium", "timeout": 30000}

class HighPrioritySource(ConfigSource):
    def get_config(self):
        return {"browser": "firefox"}

class HighestPrioritySource(ConfigSource):
    def get_config(self):
        return {"browser": "webkit", "headless": True}

class EmptySource(ConfigSource):
    def get_config(self):
        return {}

class PartialOverrideSource(ConfigSource):
    def get_config(self):
        return {"timeout": 60000}

class FailingSource(ConfigSource):
    def get_config(self):
        raise FileNotFoundError("File missing!")

# --- Step 17: SourceSpec Tests ---

def test_source_spec_stores_source_and_policy():
    source = LowPrioritySource()
    spec = SourceSpec(source=source, failure_policy=FailurePolicy.REQUIRED)
    assert spec.source is source
    assert spec.failure_policy == FailurePolicy.REQUIRED

def test_required_source_spec_propagates_failure():
    with pytest.raises(FileNotFoundError, match="File missing!"):
        resolve_config([
            SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
            SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.REQUIRED),
        ])

def test_optional_source_spec_isolates_failure():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.OPTIONAL),
    ])
    assert result["browser"] == "chromium"
    assert result["timeout"] == 30000

def test_resolver_accepts_multiple_source_specs():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
    ])
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_caller_ordering_is_preserved_with_specs():
    low = FakeConfigSource({"browser": "chromium"})
    high = FakeConfigSource({"browser": "firefox"})
    result = resolve_config([
        SourceSpec(source=high, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=low, failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["browser"] == "chromium"

# --- Existing Resolver Tests (Updated for SourceSpec) ---

def test_no_sources_returns_empty_dict():
    result = resolve_config([])
    assert result == {}

def test_single_source():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result == {"browser": "chromium", "timeout": 30000}

def test_two_sources_with_override():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_three_sources_with_highest_priority():
    sources = [
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighestPrioritySource(), failure_policy=FailurePolicy.REQUIRED)
    ]
    result = resolve_config(sources)
    assert result["browser"] == "webkit"
    assert result["headless"] is True
    assert result["timeout"] == 30000

def test_empty_source_does_not_break_merge():
    sources = [
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=EmptySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED)
    ]
    result = resolve_config(sources)
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_partial_overrides_merge_correctly():
    sources = [
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=PartialOverrideSource(), failure_policy=FailurePolicy.REQUIRED)
    ]
    result = resolve_config(sources)
    assert result["browser"] == "chromium"
    assert result["timeout"] == 60000

def test_source_dictionaries_not_mutated():
    low = LowPrioritySource()
    high = HighPrioritySource()
    
    low_copy = low.get_config().copy()
    high_copy = high.get_config().copy()
    
    _ = resolve_config([
        SourceSpec(source=low, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=high, failure_policy=FailurePolicy.REQUIRED)
    ])
    
    assert low.get_config() == low_copy
    assert high.get_config() == high_copy

def test_resolver_works_with_arbitrary_config_source():
    class CustomSource(ConfigSource):
        def get_config(self):
            return {"custom_key": "custom_value"}
            
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=CustomSource(), failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["custom_key"] == "custom_value"
    assert result["browser"] == "chromium"

def test_source_exception_propagates():
    with pytest.raises(FileNotFoundError, match="File missing!"):
        resolve_config([
            SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
            SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.REQUIRED)
        ])

def test_resolver_accepts_tuple_of_sources():
    sources = (
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
    )
    result = resolve_config(sources)
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_resolver_accepts_generator_of_sources():
    sources = (
        SourceSpec(source=source, failure_policy=FailurePolicy.REQUIRED)
        for source in [
            LowPrioritySource(),
            HighPrioritySource(),
        ]
    )
    result = resolve_config(sources)
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_precedence_still_works_with_iterable():
    sources = [
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=HighestPrioritySource(), failure_policy=FailurePolicy.REQUIRED)
    ]
    result = resolve_config(sources)
    assert result["browser"] == "webkit"

# ─── Step 15: Source Ordering Safety Tests ───────────────────────────────

def test_custom_source_can_override_environment():
    yaml = FakeConfigSource({"browser": "chromium", "timeout": 30000})
    env = FakeConfigSource({"browser": "firefox"})
    custom = FakeConfigSource({"browser": "webkit"})
    result = resolve_config([
        SourceSpec(source=yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=custom, failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["browser"] == "webkit"

def test_cli_can_override_custom_source():
    yaml = FakeConfigSource({"browser": "chromium"})
    env = FakeConfigSource({"browser": "firefox"})
    custom = FakeConfigSource({"browser": "webkit"})
    cli = FakeConfigSource({"browser": "chromium"})
    result = resolve_config([
        SourceSpec(source=yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=custom, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=cli, failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["browser"] == "chromium"

def test_custom_source_between_environment_and_cli():
    yaml = FakeConfigSource({"browser": "chromium", "timeout": 30000})
    env = FakeConfigSource({"timeout": 60000})
    custom = FakeConfigSource({"timeout": 90000})
    cli = FakeConfigSource({"browser": "webkit"})
    result = resolve_config([
        SourceSpec(source=yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=custom, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=cli, failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["timeout"] == 90000

def test_resolver_respects_caller_order():
    low = FakeConfigSource({"browser": "chromium"})
    high = FakeConfigSource({"browser": "firefox"})
    result = resolve_config([
        SourceSpec(source=high, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=low, failure_policy=FailurePolicy.REQUIRED)
    ])
    assert result["browser"] == "chromium"

# ─── Step 16: Failure Policy Tests ───────────────────────────────────────

def test_required_source_failure_propagates():
    with pytest.raises(FileNotFoundError, match="File missing!"):
        resolve_config([
            SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
            SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.REQUIRED),
        ])

def test_optional_source_failure_does_not_stop_resolution():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.OPTIONAL),
    ])
    assert result["browser"] == "chromium"
    assert result["timeout"] == 30000

def test_optional_failure_does_not_prevent_cli():
    result = resolve_config([
        SourceSpec(source=LowPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=HighPrioritySource(), failure_policy=FailurePolicy.REQUIRED),
    ])
    assert result["browser"] == "firefox"
    assert result["timeout"] == 30000

def test_optional_failure_logs_warning(caplog):
    with caplog.at_level("WARNING"):
        result = resolve_config([
            SourceSpec(source=FailingSource(), failure_policy=FailurePolicy.OPTIONAL)
        ])
    assert result == {}
    assert "Optional configuration source" in caplog.text

def test_optional_source_returning_none_does_not_stop_resolution():
    invalid_source = FakeConfigSource(None)
    valid_source = LowPrioritySource()

    result = resolve_config([
        SourceSpec(
            source=invalid_source,
            failure_policy=FailurePolicy.OPTIONAL,
        ),
        SourceSpec(
            source=valid_source,
            failure_policy=FailurePolicy.REQUIRED,
        ),
    ])

    assert result == {
        "browser": "chromium",
        "timeout": 30000,
    }


def test_resolved_config_does_not_share_nested_mutable_values():
    original_config = {
        "custom": {
            "options": ["one", "two"]
        }
    }
    source = FakeConfigSource(original_config)

    result = resolve_config([
        SourceSpec(
            source=source,
            failure_policy=FailurePolicy.REQUIRED,
        )
    ])

    result["custom"]["options"].append("three")

    assert original_config == {
        "custom": {
            "options": ["one", "two"]
        }
    }
