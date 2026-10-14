import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.pipeline_builder import build_standard_pipeline, build_test_pipeline
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource
from framework.config.environment import Environment
from framework.config.resolver import resolve_config
from framework.config.settings import Settings

def test_1_standard_pipeline_still_works(monkeypatch, tmp_path):
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
    
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    
    sources = build_standard_pipeline(str(yaml_file), Environment.STAGING, cli_args=[])
    result = resolve_config(sources)
    
    assert result["browser"] == "chromium"
    assert result["base_url"] == "https://staging.com"

def test_2_test_pipeline_has_three_sources():
    sources = build_test_pipeline({"base_url": "https://test.com"}, cli_args=[])
    assert len(sources) == 3
    assert all(isinstance(s, SourceSpec) for s in sources)

def test_3_test_pipeline_source_types():
    sources = build_test_pipeline({"base_url": "https://test.com"}, cli_args=[])
    assert isinstance(sources[0].source, FakeConfigSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_4_test_pipeline_policies():
    sources = build_test_pipeline({"base_url": "https://test.com"}, cli_args=[])
    assert sources[0].failure_policy == FailurePolicy.REQUIRED  # FakeConfig
    assert sources[1].failure_policy == FailurePolicy.OPTIONAL  # ENV
    assert sources[2].failure_policy == FailurePolicy.OPTIONAL  # CLI

def test_5_test_pipeline_precedence(monkeypatch):
    fake_config = {
        "base_url": "https://test.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000
    }
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    sources = build_test_pipeline(fake_config, cli_args=["--browser", "webkit"])
    result = resolve_config(sources)
    
    # CLI overrides ENV and FakeConfig
    assert result["browser"] == "webkit"

def test_6_test_pipeline_without_cli(monkeypatch):
    fake_config = {
        "base_url": "https://test.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000
    }
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    sources = build_test_pipeline(fake_config, cli_args=[])
    result = resolve_config(sources)
    
    # ENV overrides FakeConfig because CLI is absent
    assert result["browser"] == "firefox"

def test_7_resolver_is_shared():
    # Prove both pipelines use the exact same resolve_config function
    std_sources = build_standard_pipeline("qa-engine.yaml", Environment.STAGING, cli_args=[])
    test_sources = build_test_pipeline({"base_url": "https://test.com"}, cli_args=[])
    
    # Both should execute without error through the same resolver
    assert resolve_config(std_sources) is not None
    assert resolve_config(test_sources) is not None

def test_8_settings_remains_shared():
    # Resolve a test pipeline configuration
    fake_config = {
        "base_url": "https://test.com",
        "browser": "firefox",
        "headless": True,
        "timeout": 10000
    }
    sources = build_test_pipeline(fake_config, cli_args=[])
    resolved = resolve_config(sources)
    
    # Pass it to the standard Settings validation
    settings = Settings.from_config(resolved)
    
    assert settings.BASE_URL == "https://test.com"
    assert settings.BROWSER == "firefox"
    assert settings.TIMEOUT == 10000