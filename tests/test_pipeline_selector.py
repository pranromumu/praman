import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.pipeline_selector import select_pipeline
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource
from framework.config.environment import Environment
from framework.config.resolver import resolve_config

def test_1_standard_selects_build_standard_pipeline():
    sources = select_pipeline("standard", file_path="qa-engine.yaml", env=Environment.STAGING, cli_args=[])
    # Verify it selected the standard pipeline by checking the first source type
    assert isinstance(sources[0].source, YAMLSource)

def test_2_test_selects_build_test_pipeline():
    sources = select_pipeline("test", fake_config={"base_url": "https://test.com"}, cli_args=[])
    # Verify it selected the test pipeline by checking the first source type
    assert isinstance(sources[0].source, FakeConfigSource)

def test_3_standard_selection_produces_correct_order():
    sources = select_pipeline("standard", file_path="qa-engine.yaml", env=Environment.STAGING, cli_args=[])
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_4_test_selection_produces_correct_order():
    sources = select_pipeline("test", fake_config={"base_url": "https://test.com"}, cli_args=[])
    assert isinstance(sources[0].source, FakeConfigSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_5_standard_pipeline_resolves(monkeypatch, tmp_path):
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
    
    sources = select_pipeline("standard", file_path=str(yaml_file), env=Environment.STAGING, cli_args=[])
    result = resolve_config(sources)
    assert result["browser"] == "chromium"
    assert result["base_url"] == "https://staging.com"

def test_6_test_pipeline_resolves(monkeypatch):
    fake_config = {
        "base_url": "https://test.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000
    }
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    sources = select_pipeline("test", fake_config=fake_config, cli_args=[])
    result = resolve_config(sources)
    
    # ENV overrides FakeConfig because CLI is absent
    assert result["browser"] == "firefox"
    assert result["base_url"] == "https://test.com"

def test_7_unknown_pipeline_raises_error():
    with pytest.raises(ValueError, match="Unknown pipeline name: 'unknown'"):
        select_pipeline("unknown", cli_args=[])

def test_8_selector_does_not_modify_resolver():
    # Verify the resolver signature hasn't been modified to accept pipeline names
    sig = inspect.signature(resolve_config)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "sources"