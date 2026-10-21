import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.yaml_source import YAMLSource
from framework.config.environment import Environment


def test_valid_staging_configuration(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()
    
    assert config["base_url"] == "https://staging.client.com"
    assert config["headless"] is True
    assert config["timeout"] == 30000

def test_valid_development_configuration(tmp_path):
    yaml_content = """
environments:
  development:
    base_url: "https://dev.client.com"
    headless: false
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.DEVELOPMENT)
    config = source.get_config()
    
    assert config["base_url"] == "https://dev.client.com"
    assert config["headless"] is False
    assert config["timeout"] == 30000

def test_multiple_environments_return_requested_configuration(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    timeout: 30000
  development:
    base_url: "https://dev.client.com"
    timeout: 10000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()

    assert config["base_url"] == "https://staging.client.com"
    assert config["timeout"] == 30000
    assert "development" not in config

def test_multiple_environments_return_development_configuration(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    timeout: 30000
  development:
    base_url: "https://dev.client.com"
    timeout: 10000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.DEVELOPMENT)
    config = source.get_config()

    assert config["base_url"] == "https://dev.client.com"
    assert config["timeout"] == 10000
    assert "staging" not in config

def test_unrelated_environment_does_not_affect_staging_configuration(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    timeout: 30000
  development:
    base_url: "https://dev.client.com"
    timeout: 10000
  production:
    base_url: "https://production.client.com"
    timeout: 60000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()

    assert config == {
        "base_url": "https://staging.client.com",
        "timeout": 30000,
    }

def test_nested_configuration_values_are_preserved(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    browser:
      name: chromium
      options:
        - headless
        - slow_mo
    retries:
      count: 3
"""
    temp_file = tmp_path / "nested-staging.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()

    assert config["base_url"] == "https://staging.client.com"
    assert config["browser"] == {
        "name": "chromium",
        "options": ["headless", "slow_mo"],
    }
    assert config["retries"] == {"count": 3}

def test_yaml_scalar_types_are_preserved(tmp_path):
    yaml_content = """
environments:
  staging:
    enabled: true
    retries: 3
    threshold: 0.75
    label: "staging"
"""
    temp_file = tmp_path / "scalar-types.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()

    assert config["enabled"] is True
    assert type(config["retries"]) is int
    assert config["retries"] == 3
    assert type(config["threshold"]) is float
    assert config["threshold"] == 0.75
    assert config["label"] == "staging"

def test_utf8_bom_configuration_loads_successfully(tmp_path):
    yaml_content = """environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content, encoding="utf-8-sig")

    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()

    assert config["base_url"] == "https://staging.client.com"
    assert config["headless"] is True
    assert config["timeout"] == 30000


def test_missing_file_raises_error(tmp_path):
    source = YAMLSource(str(tmp_path / "nonexistent.yaml"), Environment.STAGING)
    
    with pytest.raises(FileNotFoundError, match="Praman configuration file not found"):
        source.get_config()


def test_empty_file_raises_error(tmp_path):
    temp_file = tmp_path / "empty.yaml"
    temp_file.write_text("", encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration file .* is empty\.",
    ):
        source.get_config()

def test_comment_only_file_raises_error(tmp_path):
    temp_file = tmp_path / "comments.yaml"
    temp_file.write_text(
        "# Praman configuration\n# No configuration values provided\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration file .* is empty\.",
    ):
        source.get_config()


def test_null_yaml_document_raises_error(tmp_path):
    temp_file = tmp_path / "null.yaml"
    temp_file.write_text("null\n", encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration file .* is empty\.",
    ):
        source.get_config()


def test_invalid_yaml_raises_error(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com
    headless: true
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    with pytest.raises(ValueError, match="Error parsing YAML"):
        source.get_config()

def test_missing_environments_raises_error(tmp_path):
    yaml_content = 'base_url: "https://dev.client.com"'
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    with pytest.raises(ValueError, match="Missing or invalid 'environments' key"):
        source.get_config()

def test_invalid_environments_type_raises_error(tmp_path):
    yaml_content = "environments: just_a_string"
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    with pytest.raises(ValueError, match="Missing or invalid 'environments' key"):
        source.get_config()

def test_null_environments_raises_clear_error(tmp_path):
    temp_file = tmp_path / "null-environments.yaml"
    temp_file.write_text(
        "environments: null\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Missing or invalid 'environments' key",
    ):
        source.get_config()

def test_empty_environments_mapping_raises_error(tmp_path):
    temp_file = tmp_path / "empty-environments.yaml"
    temp_file.write_text(
        "environments: {}\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration for environment 'staging' not found",
    ):
        source.get_config()

def test_null_environment_configuration_raises_error(tmp_path):
    temp_file = tmp_path / "null-staging.yaml"
    temp_file.write_text(
        "environments:\n  staging: null\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration for environment 'staging' not found",
    ):
        source.get_config()

def test_numeric_environment_configuration_raises_error(tmp_path):
    temp_file = tmp_path / "numeric-staging.yaml"
    temp_file.write_text(
        "environments:\n  staging: 42\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration for environment 'staging' must be a dictionary",
    ):
        source.get_config()

def test_boolean_environment_configuration_raises_error(tmp_path):
    temp_file = tmp_path / "boolean-staging.yaml"
    temp_file.write_text(
        "environments:\n  staging: true\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Configuration for environment 'staging' must be a dictionary",
    ):
        source.get_config()


def test_root_list_raises_clear_error(tmp_path):
    temp_file = tmp_path / "root-list.yaml"
    temp_file.write_text("- staging\n- development\n", encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Missing or invalid 'environments' key",
    ):
        source.get_config()


def test_numeric_root_raises_clear_error(tmp_path):
    temp_file = tmp_path / "numeric-root.yaml"
    temp_file.write_text("42\n", encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Missing or invalid 'environments' key",
    ):
        source.get_config()


def test_string_root_raises_clear_error(tmp_path):
    temp_file = tmp_path / "string-root.yaml"
    temp_file.write_text('"staging configuration"\n', encoding="utf-8")

    source = YAMLSource(str(temp_file), Environment.STAGING)

    with pytest.raises(
        ValueError,
        match=r"Missing or invalid 'environments' key",
    ):
        source.get_config()


def test_missing_requested_environment_raises_error(tmp_path):
    yaml_content = """
environments:
  development:
    base_url: "https://dev.client.com"
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    with pytest.raises(ValueError, match="Configuration for environment 'staging' not found"):
        source.get_config()

def test_environment_not_a_dictionary_raises_error(tmp_path):
    yaml_content = """
environments:
  staging: "https://staging.client.com"
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    with pytest.raises(ValueError, match="must be a dictionary"):
        source.get_config()

def test_negative_timeout_is_returned_not_rejected(tmp_path):
    """This proves YAMLSource does NOT do business validation."""
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: -500
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    config = source.get_config()
    
    # YAMLSource should return -500 without rejecting it!
    assert config["timeout"] == -500

def test_yaml_source_is_config_source(tmp_path):
    yaml_content = """
environments:
  staging:
    base_url: "https://staging.client.com"
    headless: true
    timeout: 30000
"""
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(yaml_content)
    
    source = YAMLSource(str(temp_file), Environment.STAGING)
    
    # Prove it inherits from ConfigSource
    from framework.contracts.config_source import ConfigSource
    assert isinstance(source, ConfigSource)

def test_yaml_source_reads_updated_file_contents(tmp_path):
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(
        "environments:\n  staging:\n    timeout: 10000\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    first_config = source.get_config()
    assert first_config["timeout"] == 10000

    temp_file.write_text(
        "environments:\n  staging:\n    timeout: 20000\n",
        encoding="utf-8",
    )

    second_config = source.get_config()

    assert second_config["timeout"] == 20000

def test_yaml_source_returns_fresh_configuration_dict(tmp_path):
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(
        "environments:\n  staging:\n    timeout: 10000\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    first_config = source.get_config()
    first_config["timeout"] = 99999

    second_config = source.get_config()

    assert second_config["timeout"] == 10000
    assert second_config is not first_config

def test_yaml_source_instances_select_environments_independently(tmp_path):
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(
        "environments:\n"
        "  staging:\n"
        "    base_url: 'https://staging.example.com'\n"
        "    timeout: 10000\n"
        "  development:\n"
        "    base_url: 'https://dev.example.com'\n"
        "    timeout: 5000\n",
        encoding="utf-8",
    )

    staging_source = YAMLSource(str(temp_file), Environment.STAGING)
    development_source = YAMLSource(str(temp_file), Environment.DEVELOPMENT)

    staging_config = staging_source.get_config()
    development_config = development_source.get_config()

    assert staging_config["base_url"] == "https://staging.example.com"
    assert staging_config["timeout"] == 10000

    assert development_config["base_url"] == "https://dev.example.com"
    assert development_config["timeout"] == 5000

    # Reading development must not change staging's configuration.
    assert staging_source.get_config()["timeout"] == 10000

def test_yaml_source_nested_mutations_do_not_persist_between_reads(tmp_path):
    temp_file = tmp_path / "qa-engine.yaml"
    temp_file.write_text(
        "environments:\n"
        "  staging:\n"
        "    browser:\n"
        "      name: chromium\n"
        "      options:\n"
        "        - headless\n"
        "    retries:\n"
        "      count: 3\n",
        encoding="utf-8",
    )

    source = YAMLSource(str(temp_file), Environment.STAGING)

    first_config = source.get_config()
    first_config["browser"]["name"] = "firefox"
    first_config["browser"]["options"].append("debug")
    first_config["retries"]["count"] = 99

    second_config = source.get_config()

    assert second_config["browser"]["name"] == "chromium"
    assert second_config["browser"]["options"] == ["headless"]
    assert second_config["retries"]["count"] == 3