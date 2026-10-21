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