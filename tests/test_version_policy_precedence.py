import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.settings import Settings
from framework.config.environment import Environment
from framework.config.composition import resolve_praman_config
from framework.compatibility.composition import build_compatibility_registry, build_version_policy_factory
from framework.config.legacy_v1_source import LegacyV1Source
from framework.compatibility.versioned_source import VersionedSource
from framework.compatibility.policies.version_selection import LowestVersionPolicy

@pytest.fixture
def tmp_yaml(tmp_path):
    file_path = tmp_path / "qa-engine.yaml"
    def write(content):
        file_path.write_text(content)
    return file_path, write

def test_1_default_policy_when_no_source_specifies(tmp_yaml):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
""")
    settings = Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=[])
    assert settings.VERSION_POLICY == "highest"

def test_2_yaml_overrides_default(tmp_yaml):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: lowest
""")
    settings = Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=[])
    assert settings.VERSION_POLICY == "lowest"

def test_3_env_overrides_yaml(tmp_yaml, monkeypatch):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: lowest
""")
    monkeypatch.setenv("PRAMAN_VERSION_POLICY", "highest")
    settings = Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=[])
    assert settings.VERSION_POLICY == "highest"

def test_4_cli_overrides_env(tmp_yaml, monkeypatch):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: highest
""")
    monkeypatch.setenv("PRAMAN_VERSION_POLICY", "highest")
    cli_args = ["--version-policy", "lowest"]
    
    settings = Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=cli_args)
    assert settings.VERSION_POLICY == "lowest"

def test_5_invalid_policy_name_fails_clearly(tmp_yaml):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: middle
""")
    # FIXED: Validation now happens at Settings loading, which is exactly what we want!
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=[])

def test_6_effective_policy_reaches_negotiate_contract(tmp_yaml, monkeypatch):
    file_path, write = tmp_yaml
    write("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: highest
""")
    monkeypatch.setenv("PRAMAN_VERSION_POLICY", "highest")
    cli_args = ["--version-policy", "lowest"]
    
    settings = Settings.from_config_file(str(file_path), Environment.STAGING, cli_args=cli_args)
    
    registry = build_compatibility_registry()
    factory = build_version_policy_factory()
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    
    with patch("framework.config.composition.negotiate_contract") as mock_negotiate:
        mock_negotiate.return_value = MagicMock()
        mock_negotiate.return_value.get_config.return_value = {
            "base_url": "https://staging.com",
            "browser": "chromium",
            "headless": True,
            "timeout": 30000,
        }
        resolve_praman_config(
            versioned_source=vs,
            praman_supported_versions=[2],
            environment="prod",
            registry=registry,
            policy_factory=factory,
            version_policy_name=settings.VERSION_POLICY
        )
        
        # Verify that negotiate_contract actually received the LowestVersionPolicy instance
        kwargs = mock_negotiate.call_args.kwargs
        assert isinstance(kwargs["version_policy"], LowestVersionPolicy)
