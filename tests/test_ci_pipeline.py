import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.pipeline_builder import build_ci_pipeline
from framework.config.pipeline_registry import PIPELINE_REGISTRY
from framework.config.pipeline_selector import select_pipeline
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.fake_source import FakeConfigSource
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.resolver import resolve_config

def test_1_ci_builder_exists():
    assert callable(build_ci_pipeline)

def test_2_dependencies_are_passed_in():
    yaml = FakeConfigSource({"base_url": "https://yaml.com"})
    env = FakeConfigSource({"browser": "firefox"})
    github = FakeConfigSource({"api_key": "12345"})
    cli = FakeConfigSource({"browser": "webkit"})
    
    # We pass the objects IN, we don't pass file paths for the builder to construct
    specs = build_ci_pipeline(yaml, env, github, cli)
    assert len(specs) == 4
    assert specs[0].source is yaml
    assert specs[1].source is env
    assert specs[2].source is github
    assert specs[3].source is cli

def test_3_builder_does_not_construct_dependencies():
    # Read source code to prove it doesn't call YAMLSource() or EnvSource() etc.
    source_code = inspect.getsource(build_ci_pipeline)
    assert "YAMLSource(" not in source_code
    assert "EnvSource(" not in source_code
    assert "CLISource(" not in source_code
    assert "FakeConfigSource(" not in source_code

def test_4_correct_failure_policies():
    yaml = FakeConfigSource({"base_url": "https://yaml.com"})
    env = FakeConfigSource({})
    github = FakeConfigSource({})
    cli = FakeConfigSource({})
    
    specs = build_ci_pipeline(yaml, env, github, cli)
    assert specs[0].failure_policy == FailurePolicy.REQUIRED  # YAML
    assert specs[1].failure_policy == FailurePolicy.OPTIONAL  # ENV
    assert specs[2].failure_policy == FailurePolicy.REQUIRED  # GITHUB
    assert specs[3].failure_policy == FailurePolicy.OPTIONAL  # CLI

def test_5_correct_ordering():
    yaml = FakeConfigSource({"base_url": "https://yaml.com"})
    env = FakeConfigSource({})
    github = FakeConfigSource({})
    cli = FakeConfigSource({})
    
    specs = build_ci_pipeline(yaml, env, github, cli)
    # Verify they are the exact objects we passed in, in the exact order
    assert specs[0].source is yaml
    assert specs[1].source is env
    assert specs[2].source is github
    assert specs[3].source is cli

def test_6_resolver_remains_unchanged():
    sig = inspect.signature(resolve_config)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "sources"

def test_8_unit_tests_can_inject_fakes():
    # The whole test suite uses FakeConfigSource to verify assembly without I/O
    yaml = FakeConfigSource({"base_url": "https://yaml.com", "browser": "chromium", "headless": True, "timeout": 30000})
    env = FakeConfigSource({"browser": "firefox"})
    github = FakeConfigSource({})
    cli = FakeConfigSource({"browser": "webkit"})
    
    specs = build_ci_pipeline(yaml, env, github, cli)
    result = resolve_config(specs)
    
    assert result["browser"] == "webkit"  # CLI won
    assert result["base_url"] == "https://yaml.com" # YAML survived

def test_9_registry_points_to_ci_builder():
    assert "ci" in PIPELINE_REGISTRY
    assert PIPELINE_REGISTRY["ci"] is build_ci_pipeline
    
    # Verify the selector can invoke it via DI
    yaml = FakeConfigSource({"base_url": "https://yaml.com", "browser": "chromium", "headless": True, "timeout": 30000})
    env = FakeConfigSource({})
    github = FakeConfigSource({})
    cli = FakeConfigSource({"browser": "webkit"})
    
    specs = select_pipeline(
        "ci", 
        yaml_source=yaml, 
        env_source=env, 
        github_source=github, 
        cli_source=cli
    )
    assert len(specs) == 4
    assert specs[3].source is cli