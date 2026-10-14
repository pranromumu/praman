import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.settings import Settings
from framework.config.environment import Environment
from framework.compatibility.composition import build_version_policy_factory

def test_1_highest_accepted_in_settings():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "highest"}
    settings = Settings.from_config(config)
    assert settings.VERSION_POLICY == "highest"

def test_2_lowest_accepted_in_settings():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "lowest"}
    settings = Settings.from_config(config)
    assert settings.VERSION_POLICY == "lowest"

def test_3_middle_rejected_during_settings_loading():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "middle"}
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        Settings.from_config(config)

def test_4_empty_policy_rejected_in_settings():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": ""}
    with pytest.raises(ValueError, match="VERSION_POLICY must be a non-empty string"):
        Settings.from_config(config)

def test_5_non_string_policy_rejected_in_settings():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": 123}
    with pytest.raises(ValueError):
        Settings.from_config(config)

def test_6_direct_factory_call_rejects_middle():
    factory = build_version_policy_factory()
    with pytest.raises(ValueError, match="Unknown policy name: 'middle'"):
        factory.create_policy("middle")

def test_7_yaml_env_cli_precedence_still_passes(tmp_path, monkeypatch):
    file_path = tmp_path / "qa-engine.yaml"
    file_path.write_text("""
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

def test_8_middle_rejected_when_provider_injected_into_from_config():
    factory = build_version_policy_factory()
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "middle"}
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        Settings.from_config(config, policy_name_provider=factory)

def test_9_middle_rejected_when_provider_injected_into_from_config_file(tmp_path):
    file_path = tmp_path / "qa-engine.yaml"
    file_path.write_text("""
environments:
  staging:
    base_url: "https://staging.com"
    browser: chromium
    headless: true
    timeout: 30000
    version_policy: middle
""")
    factory = build_version_policy_factory()
    
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        Settings.from_config_file(
            str(file_path),
            Environment.STAGING,
            cli_args=[],
            policy_name_provider=factory
        )



from framework.compatibility.policies.policy_name_provider import PolicyNameProvider

# A custom provider that claims "middle" is a supported policy
class CustomTestProvider(PolicyNameProvider):
    def get_supported_policy_names(self) -> list[str]:
        return ["highest", "lowest", "middle"]

# NEW: Task 5 Tests
def test_10_custom_provider_accepts_middle():
    provider = CustomTestProvider()
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "middle"}
    
    # Should succeed because the custom provider supports "middle"
    settings = Settings.from_config(config, policy_name_provider=provider)
    assert settings.VERSION_POLICY == "middle"

def test_11_default_provider_still_rejects_middle():
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000, "version_policy": "middle"}
    
    # Should fail because the default production factory only supports "highest" and "lowest"
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        Settings.from_config(config)