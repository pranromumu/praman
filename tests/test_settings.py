import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import dataclasses
from framework.config.environment import Environment
from framework.config.settings import Settings

# ─── Existing Happy Path Tests ───────────────────────────────────────────

def test_development_resolves_from_yaml():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.DEVELOPMENT, cli_args=[])
    assert settings.BASE_URL == "https://dev.client.com"
    assert settings.HEADLESS is False
    assert settings.TIMEOUT == 30000
    assert settings.BROWSER == "chromium"

def test_staging_resolves_from_yaml():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 30000
    assert settings.BROWSER == "chromium"

def test_production_resolves_from_yaml():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.PRODUCTION, cli_args=[])
    assert settings.BASE_URL == "https://client.com"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 30000
    assert settings.BROWSER == "chromium"

# ─── Structural Validation Tests ─────────────────────────────────────────

def test_missing_environments_key_raises_error(tmp_path):
    yaml_content = 'base_url: "https://dev.client.com"'
    temp_file = tmp_path / "missing-envs.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Missing or invalid 'environments' key"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_environment_not_a_dictionary_raises_error(tmp_path):
    yaml_content = """
environments:
  staging: "https://staging.client.com"
"""
    temp_file = tmp_path / "string-env.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="must be a dictionary"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

# ─── Schema Validation Tests ─────────────────────────────────────────────

def test_unknown_field_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
    unexpected_setting: "something"
"""
    temp_file = tmp_path / "unknown.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Unexpected configuration field"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_typo_raises_error_with_suggestion(tmp_path):
    yaml_content = """
environments:
  staging:
    baseurl: "https://staging.client.com"
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "typo.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Did you mean 'base_url'?"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_missing_base_url_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "missing-url.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Missing required configuration field"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_missing_headless_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    timeout: 30000
"""
    temp_file = tmp_path / "missing-headless.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Missing required configuration field"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

def test_missing_timeout_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
"""
    temp_file = tmp_path / "missing-timeout.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="Missing required configuration field"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

# ─── Value Validation Tests ─────────────────────────────────────────────

def test_invalid_empty_base_url_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: ""
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "empty-url.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError, match="BASE_URL cannot be empty"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])

# ─── Error Aggregation Tests ────────────────────────────────────────────

def test_schema_and_value_errors_aggregated_together(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: ""
    headless: "yes"
    timeout: -500
    extra_field: "value"
"""
    temp_file = tmp_path / "mixed-errors.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    error_message = str(exc_info.value)
    
    assert "Unexpected configuration field: 'extra_field'" in error_message
    assert "BASE_URL cannot be empty" in error_message
    assert "HEADLESS must be a boolean" in error_message
    assert "TIMEOUT must be an integer greater than 0" in error_message

def test_multiple_value_errors_aggregated(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: ""
    headless: "false"
    timeout: "30000"
"""
    temp_file = tmp_path / "multi-value.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    error_message = str(exc_info.value)
    
    assert "BASE_URL cannot be empty" in error_message
    assert "HEADLESS must be a boolean" in error_message
    assert "TIMEOUT must be an integer greater than 0" in error_message

def test_missing_field_does_not_generate_value_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
"""
    temp_file = tmp_path / "missing-no-value.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    error_message = str(exc_info.value)
    
    assert "Missing required configuration field" in error_message
    assert "timeout" in error_message
    assert "TIMEOUT must be an integer" not in error_message

def test_complex_scenario_aggregates_all_errors(tmp_path):
    yaml_content = """
environments:
  staging:
    baseurl: ""
    headless: "yes"
    timeout: -500
    unknown_field: true
"""
    temp_file = tmp_path / "complex.yaml"
    temp_file.write_text(yaml_content)
    
    with pytest.raises(ValueError) as exc_info:
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    
    error_message = str(exc_info.value)
    
    assert "Unexpected configuration field: 'baseurl'" in error_message
    assert "Did you mean 'base_url'?" in error_message
    assert "Unexpected configuration field: 'unknown_field'" in error_message
    assert "Missing required configuration field" in error_message
    assert "base_url" in error_message
    
    assert "HEADLESS must be a boolean" not in error_message
    assert "TIMEOUT must be an integer" not in error_message

# ─── Immutability Tests ─────────────────────────────────────────────────

def test_normal_loading_still_works():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.BROWSER == "chromium"

def test_base_url_cannot_be_modified():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    original_url = settings.BASE_URL
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.BASE_URL = "https://evil.example.com"
        
    assert settings.BASE_URL == original_url

def test_browser_cannot_be_modified():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    original_browser = settings.BROWSER
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.BROWSER = "firefox"
        
    assert settings.BROWSER == original_browser

def test_headless_cannot_be_modified():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    original_headless = settings.HEADLESS
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.HEADLESS = False
        
    assert settings.HEADLESS == original_headless

def test_timeout_cannot_be_modified():
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    original_timeout = settings.TIMEOUT
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.TIMEOUT = 1000
        
    assert settings.TIMEOUT == original_timeout
# ─── Step 3: Environment Variable Override Tests ─────────────────────────

def test_yaml_only_values_used(monkeypatch):
    monkeypatch.delenv("PRAMAN_BASE_URL", raising=False)
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    monkeypatch.delenv("PRAMAN_HEADLESS", raising=False)
    monkeypatch.delenv("PRAMAN_TIMEOUT", raising=False)
    
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.BROWSER == "chromium"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 30000

def test_browser_env_override(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    
    assert settings.BROWSER == "firefox"
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.HEADLESS is True

def test_timeout_env_override(monkeypatch):
    monkeypatch.setenv("PRAMAN_TIMEOUT", "60000")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    
    assert settings.TIMEOUT == 60000
    assert settings.BASE_URL == "https://staging.client.com"

def test_multiple_env_overrides(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    monkeypatch.setenv("PRAMAN_TIMEOUT", "60000")
    
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    assert settings.BROWSER == "firefox"
    assert settings.TIMEOUT == 60000
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.HEADLESS is True

def test_env_does_not_replace_yaml(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    
    assert settings.BASE_URL == "https://staging.client.com"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 30000

def test_invalid_final_browser_rejected(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "safari")
    
    with pytest.raises(ValueError, match="BROWSER must be one of"):
        Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])

# ─── Step 4: CLI Integration Tests (Migrated to use cli_args) ────────────

def test_cli_overrides_env_and_yaml(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=["--browser", "webkit"])
    assert settings.BROWSER == "webkit"

def test_cli_absent_env_overrides_yaml(monkeypatch):
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
    assert settings.BROWSER == "firefox"

def test_cli_overrides_env_and_yaml_timeout(monkeypatch):
    monkeypatch.setenv("PRAMAN_TIMEOUT", "60000")
    settings = Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=["--timeout", "10000"])
    assert settings.TIMEOUT == 10000

def test_cli_overrides_invalid_yaml_and_env(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: safari
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "invalid-yaml.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=["--browser", "webkit"])
    assert settings.BROWSER == "webkit"

# ─── Step 6: Defaults & Architectural Boundary Tests ─────────────────────

def test_settings_applies_default_browser(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "no-browser.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    assert settings.BROWSER == "chromium"

def test_yaml_explicit_browser_wins_over_default(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: firefox
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "firefox.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    assert settings.BROWSER == "firefox"

def test_env_overrides_yaml_browser(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: firefox
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "env-overrides.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "webkit")
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])
    assert settings.BROWSER == "webkit"

def test_cli_overrides_env_and_yaml_browser(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: firefox
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "cli-overrides.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.setenv("PRAMAN_BROWSER", "webkit")
    settings = Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=["--browser", "chromium"])
    assert settings.BROWSER == "chromium"

def test_invalid_explicit_browser_rejected(monkeypatch, tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: safari
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "invalid.yaml"
    temp_file.write_text(yaml_content)
    
    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)
    with pytest.raises(ValueError, match="BROWSER must be one of"):
        Settings.from_config_file(str(temp_file), Environment.STAGING, cli_args=[])


from framework.compatibility.composition import build_version_policy_factory
from framework.compatibility.policies.policy_name_provider import PolicyNameProvider

def test_34_direct_validate_rejects_middle_without_provider():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=30000,
        VERSION_POLICY="middle"
    )
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        settings.validate()

def test_35_direct_validate_rejects_middle_with_injected_provider():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=30000,
        VERSION_POLICY="middle"
    )
    factory = build_version_policy_factory()
    with pytest.raises(ValueError, match="VERSION_POLICY must be one of"):
        settings.validate(policy_name_provider=factory)


def test_timeout_boolean_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=True,
    )

    with pytest.raises(ValueError, match="TIMEOUT must be an integer greater than 0"):
        settings.validate()


def test_timeout_false_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=False,
    )

    with pytest.raises(
        ValueError,
        match="TIMEOUT must be an integer greater than 0",
    ):
        settings.validate()

def test_timeout_negative_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=-1,
    )
    with pytest.raises(
        ValueError,
        match="TIMEOUT must be an integer greater than 0",
    ):
        settings.validate()

def test_timeout_zero_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=0,
    )
    with pytest.raises(
        ValueError,
        match="TIMEOUT must be an integer greater than 0",
    ):
        settings.validate()

def test_timeout_one_is_accepted():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=1,
    )
    settings.validate()

def test_timeout_float_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS=True,
        TIMEOUT=30000.5,
    )

    with pytest.raises(
        ValueError,
        match="TIMEOUT must be an integer greater than 0",
    ):
        settings.validate()

def test_from_config_missing_timeout_raises_error():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": True,
    }

    with pytest.raises(
        ValueError,
        match=r"Missing required configuration field\(s\): \['timeout'\]",
    ):
        Settings.from_config(config)

def test_from_config_multiple_missing_required_fields_raises_error():
    config = {
        "browser": "chromium",
    }

    with pytest.raises(ValueError) as exc_info:
        Settings.from_config(config)

    error_message = str(exc_info.value)

    assert "Missing required configuration field(s)" in error_message
    assert "'base_url'" in error_message
    assert "'headless'" in error_message
    assert "'timeout'" in error_message

def test_from_config_unknown_field_raises_error():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
        "browzer": "chromium",
    }

    with pytest.raises(
        ValueError,
        match=r"Unexpected configuration field: 'browzer'",
    ):
        Settings.from_config(config)


def test_from_config_mixed_type_unknown_keys_raise_validation_error():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
        7: "unexpected",
        None: "also unexpected",
    }

    with pytest.raises(ValueError) as exc_info:
        Settings.from_config(config)

    error_message = str(exc_info.value)

    assert "Unexpected configuration field: '7'" in error_message
    assert "Unexpected configuration field: 'None'" in error_message


def test_from_config_baseurl_typo_suggests_base_url():
    config = {
        "baseurl": "https://example.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
    }

    with pytest.raises(ValueError) as exc_info:
        Settings.from_config(config)

    error_message = str(exc_info.value)

    assert "Unexpected configuration field: 'baseurl'" in error_message
    assert "Did you mean 'base_url'?" in error_message

def test_from_config_valid_config_returns_settings():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
    }

    settings = Settings.from_config(config)

    assert isinstance(settings, Settings)
    assert settings.BASE_URL == "https://example.com"
    assert settings.BROWSER == "chromium"
    assert settings.HEADLESS is True
    assert settings.TIMEOUT == 30000

def test_from_config_numeric_base_url_raises_error():
    config = {
        "base_url": 123,
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
    }

    with pytest.raises(
        ValueError,
        match=r"BASE_URL must be a string",
    ):
        Settings.from_config(config)


def test_from_config_whitespace_base_url_raises_error():
    config = {
        "base_url": "   ",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
    }

    with pytest.raises(
        ValueError,
        match=r"BASE_URL cannot be empty",
    ):
        Settings.from_config(config)


def test_from_config_valid_version_policy_is_applied():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": True,
        "timeout": 30000,
        "version_policy": "highest",
    }

    settings = Settings.from_config(config)

    assert isinstance(settings, Settings)
    assert settings.VERSION_POLICY == "highest"

def test_from_config_invalid_browser_raises_error():
    config = {
        "base_url": "https://example.com",
        "browser": "safari",
        "headless": True,
        "timeout": 30000,
    }

    with pytest.raises(
        ValueError,
        match=r"BROWSER must be one of .*but got 'safari'\.",
    ):
        Settings.from_config(config)


def test_from_config_invalid_headless_raises_error():
    config = {
        "base_url": "https://example.com",
        "browser": "chromium",
        "headless": "yes",
        "timeout": 30000,
    }

    with pytest.raises(
        ValueError,
        match=r"HEADLESS must be a boolean \(True/False\), but got str\.",
    ):
        Settings.from_config(config)

def test_non_string_browser_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER=123,
        HEADLESS=True,
        TIMEOUT=30000,
    )

    with pytest.raises(
        ValueError,
        match="BROWSER must be a string",
    ):
        settings.validate()

def test_non_boolean_headless_is_rejected():
    settings = Settings(
        BASE_URL="https://example.com",
        BROWSER="chromium",
        HEADLESS="yes",
        TIMEOUT=30000,
    )

    with pytest.raises(
        ValueError,
        match="HEADLESS must be a boolean",
    ):
        settings.validate()

@pytest.mark.parametrize(
    "invalid_config",
    [
        None,
        [],
        "invalid",
        123,
    ],
)
def test_from_config_rejects_non_dictionary_input(invalid_config):
    with pytest.raises(
        ValueError,
        match="Configuration must be a dictionary",
    ):
        Settings.from_config(invalid_config)



def test_project_228_cli_overrides_environment(tmp_path, monkeypatch):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    config_file = tmp_path / "cli-precedence.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")

    settings = Settings.from_config_file(
        str(config_file),
        Environment.STAGING,
        cli_args=["--browser", "webkit"],
    )

    assert settings.BROWSER == "webkit"


def test_project_228_environment_overrides_yaml(tmp_path, monkeypatch):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    config_file = tmp_path / "env-precedence.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")

    settings = Settings.from_config_file(
        str(config_file),
        Environment.STAGING,
    )

    assert settings.BROWSER == "firefox"


def test_project_228_yaml_overrides_defaults(tmp_path, monkeypatch):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: firefox
    headless: true
    timeout: 30000
"""
    config_file = tmp_path / "yaml-precedence.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    monkeypatch.delenv("PRAMAN_BROWSER", raising=False)

    settings = Settings.from_config_file(
        str(config_file),
        Environment.STAGING,
    )

    assert settings.BROWSER == "firefox"


def test_project_228_full_precedence_chain(tmp_path, monkeypatch):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser: chromium
    headless: true
    timeout: 30000
"""
    config_file = tmp_path / "full-precedence.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    monkeypatch.setenv("PRAMAN_BROWSER", "firefox")

    settings = Settings.from_config_file(
        str(config_file),
        Environment.STAGING,
        cli_args=["--browser", "webkit"],
    )

    assert settings.BROWSER == "webkit"
