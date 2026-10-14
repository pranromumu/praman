import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.source import ConfigSource
from framework.config.resolver import resolve_config
from framework.config.settings import Settings
from framework.config.failure_policy import FailurePolicy
from framework.config.source_spec import SourceSpec

class FakeConfigSource(ConfigSource):
    def __init__(self, config: dict):
        self._config = config

    def get_config(self) -> dict:
        return self._config

def test_fake_source_implements_config_source():
    source = FakeConfigSource({"browser": "chromium"})
    assert isinstance(source, ConfigSource)

def test_resolver_with_fake_sources():
    fake_yaml = FakeConfigSource({"browser": "chromium", "timeout": 30000})
    fake_env = FakeConfigSource({"browser": "firefox"})
    fake_cli = FakeConfigSource({"browser": "webkit", "headless": True})
    
    result = resolve_config([
        SourceSpec(source=fake_yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=fake_env, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=fake_cli, failure_policy=FailurePolicy.OPTIONAL)
    ])
    
    assert result["browser"] == "webkit"
    assert result["timeout"] == 30000
    assert result["headless"] is True

def test_settings_from_resolved_dictionary():
    resolved_config = {
        "base_url": "https://test.example.com",
        "browser": "firefox",
        "headless": True,
        "timeout": 10000,
    }
    settings = Settings.from_config(resolved_config)
    assert settings.BASE_URL == "https://test.example.com"
    assert settings.BROWSER == "firefox"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 10000

def test_full_pipeline_with_fake_sources():
    fake_yaml = FakeConfigSource({
        "base_url": "https://yaml.example.com", 
        "browser": "chromium", 
        "headless": True, 
        "timeout": 30000
    })
    fake_env = FakeConfigSource({
        "browser": "firefox", 
        "headless": False
    })
    fake_cli = FakeConfigSource({
        "browser": "webkit"
    })
    
    resolved = resolve_config([
        SourceSpec(source=fake_yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=fake_env, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=fake_cli, failure_policy=FailurePolicy.OPTIONAL)
    ])
    settings = Settings.from_config(resolved)
    
    assert settings.BASE_URL == "https://yaml.example.com"
    assert settings.BROWSER == "webkit"
    assert settings.HEADLESS is False
    assert settings.TIMEOUT == 30000

def test_fake_pipeline_is_independent_of_external_io(monkeypatch, tmp_path):
    real_file = tmp_path / "qa-engine.yaml"
    real_file.write_text("environments:\n  staging:\n    base_url: 'https://real.com'")
    monkeypatch.setenv("PRAMAN_BROWSER", "safari")
    
    fake_yaml = FakeConfigSource({
        "base_url": "https://fake.com", 
        "browser": "chromium", 
        "headless": True, 
        "timeout": 5000
    })
    fake_env = FakeConfigSource({})
    fake_cli = FakeConfigSource({})
    
    resolved = resolve_config([
        SourceSpec(source=fake_yaml, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=fake_env, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=fake_cli, failure_policy=FailurePolicy.OPTIONAL)
    ])
    settings = Settings.from_config(resolved)
    
    assert settings.BASE_URL == "https://fake.com"
    assert settings.BROWSER == "chromium"
    assert settings.TIMEOUT == 5000