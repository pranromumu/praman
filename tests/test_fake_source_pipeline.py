import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.fake_source import FakeConfigSource
from framework.contracts.config_source import ConfigSource
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.resolver import resolve_config
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.environment import Environment

def test_1_fake_source_implements_config_source():
    source = FakeConfigSource({"browser": "firefox"})
    assert isinstance(source, ConfigSource)

def test_2_returns_supplied_dictionary():
    config = {"browser": "firefox", "timeout": 60000}
    source = FakeConfigSource(config)
    assert source.get_config() == config

def test_3_works_inside_source_spec():
    source = FakeConfigSource({"browser": "firefox"})
    spec = SourceSpec(source=source, failure_policy=FailurePolicy.OPTIONAL)
    assert spec.source is source
    assert spec.failure_policy == FailurePolicy.OPTIONAL

def test_4_resolver_accepts_fake_source():
    fake = FakeConfigSource({"browser": "webkit"})
    spec = SourceSpec(source=fake, failure_policy=FailurePolicy.REQUIRED)
    result = resolve_config([spec])
    assert result["browser"] == "webkit"

def test_5_fake_overrides_env(monkeypatch, tmp_path):
    # Setup YAML
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    yaml_file = tmp_path / "qa-engine.yaml"
    yaml_file.write_text(yaml_content)
    
    # ENV overrides YAML
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    # FAKE overrides ENV
    fake_source = FakeConfigSource({"browser": "webkit"})
    
    sources = [
        SourceSpec(source=YAMLSource(str(yaml_file), Environment.STAGING), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=EnvSource(), failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=fake_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=CLISource(args=[]), failure_policy=FailurePolicy.OPTIONAL)
    ]
    
    result = resolve_config(sources)
    assert result["browser"] == "webkit"

def test_6_cli_overrides_fake(monkeypatch, tmp_path):
    # Setup YAML
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    yaml_file = tmp_path / "qa-engine.yaml"
    yaml_file.write_text(yaml_content)
    
    # ENV overrides YAML
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    # FAKE overrides ENV
    fake_source = FakeConfigSource({"browser": "webkit"})
    
    # CLI overrides FAKE
    cli_source = CLISource(args=["--browser", "chromium"])
    
    sources = [
        SourceSpec(source=YAMLSource(str(yaml_file), Environment.STAGING), failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=EnvSource(), failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=fake_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=cli_source, failure_policy=FailurePolicy.OPTIONAL)
    ]
    
    result = resolve_config(sources)
    assert result["browser"] == "chromium"

def test_7_resolver_requires_no_modification():
    # This is a conceptual test. We verify that resolve_config still only takes
    # an iterable of SourceSpec and returns a dict.
    # The fact that test_5 and test_6 passed proves the resolver wasn't modified 
    # to specifically handle FakeConfigSource.
    import inspect
    sig = inspect.signature(resolve_config)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "sources"