import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.pipeline_builder import build_standard_pipeline
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.environment import Environment
from framework.config.resolver import resolve_config

def test_1_three_sources_are_registered():
    sources = build_standard_pipeline("qa-engine.yaml", Environment.STAGING)
    assert len(sources) == 3
    assert all(isinstance(s, SourceSpec) for s in sources)

def test_2_correct_source_types():
    sources = build_standard_pipeline("qa-engine.yaml", Environment.STAGING)
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_3_correct_failure_policies():
    sources = build_standard_pipeline("qa-engine.yaml", Environment.STAGING)
    assert sources[0].failure_policy == FailurePolicy.REQUIRED  # YAML
    assert sources[1].failure_policy == FailurePolicy.OPTIONAL  # ENV
    assert sources[2].failure_policy == FailurePolicy.OPTIONAL  # CLI

def test_4_correct_ordering():
    sources = build_standard_pipeline("qa-engine.yaml", Environment.STAGING)
    # Explicitly check the types in order
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_5_arguments_are_passed_correctly():
    file_path = "custom.yaml"
    env = Environment.PRODUCTION
    cli_args = ["--browser", "firefox"]
    
    sources = build_standard_pipeline(file_path=file_path, env=env, cli_args=cli_args)
    
    assert sources[0].source._file_path == file_path
    assert sources[0].source._env == env
    assert sources[2].source._args == cli_args

def test_6_builder_integrates_with_resolver(monkeypatch, tmp_path):
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
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    sources = build_standard_pipeline(
        file_path=str(yaml_file), 
        env=Environment.STAGING, 
        cli_args=["--browser", "webkit"]
    )
    
    result = resolve_config(sources)
    # CLI (webkit) overrides ENV (firefox) and YAML (chromium)
    assert result["browser"] == "webkit"
    assert result["base_url"] == "https://staging.com"

def test_7_resolver_remains_unchanged():
    # Verify the resolver signature hasn't been modified to accept pipeline names or builders
    sig = inspect.signature(resolve_config)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "sources"


def test_environment_overrides_yaml_when_cli_does_not_override(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.example.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    yaml_file = tmp_path / "qa-engine.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")

    sources = build_standard_pipeline(
        file_path=str(yaml_file),
        env=Environment.STAGING,
        cli_args=[],
    )

    result = resolve_config(sources)

    assert result["browser"] == "firefox"
    assert result["base_url"] == "https://staging.example.com"