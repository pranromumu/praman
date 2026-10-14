import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.environment import Environment
from framework.config.settings import Settings

# ─── Step 11: Configuration Pipeline Integration Tests ───────────────────

def test_1_yaml_only_pipeline(monkeypatch, tmp_path):
    """Test 1: YAML only -> firefox, 30000"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: firefox
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    # Ensure no env vars or CLI args interfere
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    monkeypatch.delenv("PRAMAN_TIMEOUT", raising=False)
    
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    assert settings.BROWSER == "firefox"
    assert settings.TIMEOUT == 30000

def test_2_env_overrides_yaml_pipeline(monkeypatch, tmp_path):
    """Test 2: YAML (chromium) + ENV (firefox) -> firefox"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    assert settings.BROWSER == "firefox"

def test_3_cli_overrides_env_pipeline(monkeypatch, tmp_path):
    """Test 3: YAML (chromium) + ENV (firefox) + CLI (webkit) -> webkit"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=["--browser", "webkit"])
    
    assert settings.BROWSER == "webkit"

def test_4_partial_overrides_from_multiple_sources_pipeline(monkeypatch, tmp_path):
    """Test 4: Different sources contribute different fields"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    # Clear all env vars first to ensure a clean slate
    monkeypatch.delenv("PRAMAN_BASE_URL", raising=False)
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    monkeypatch.delenv("PRAMAN_HEADLESS", raising=False)
    monkeypatch.delenv("PRAMAN_TIMEOUT", raising=False)
    
    # ENV overrides HEADLESS
    monkeypatch.setenv("PRAMAN_HEADLESS", "false")
    
    # CLI overrides BROWSER
    settings = Settings.from_config_file(
        str(temp_file), 
        Environment.STAGING, 
        cli_args=["--browser", "firefox"]
    )
    
    assert settings.BASE_URL == "https://staging.client.com"  # From YAML
    assert settings.BROWSER == "firefox"                     # From CLI
    assert settings.HEADLESS is False                        # From ENV
    assert settings.TIMEOUT == 30000                         # From YAML

def test_5_invalid_final_config_rejected_pipeline(monkeypatch, tmp_path):
    """Test 5: Invalid final configuration (ENV sets safari) -> ValueError"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "safari")
    
    with pytest.raises(ValueError, match="BROWSER must be one of"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_6_valid_override_replaces_invalid_yaml_pipeline(monkeypatch, tmp_path):
    """Test 6: Higher-priority valid value replaces lower-priority invalid value"""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: safari  # Invalid in YAML
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    # ENV overrides to firefox, CLI overrides to webkit
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    
    settings = Settings.from_config_file(
        str(temp_file), 
        Environment.STAGING, 
        cli_args=["--browser", "webkit"]
    )
    
    # The invalid safari was completely overwritten. Validation should pass.
    assert settings.BROWSER == "webkit"