import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.composition import build_config_sources
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.environment import Environment
from framework.config.settings import Settings

def test_1_three_sources_are_registered():
    sources = build_config_sources("qa-engine.yaml", Environment.STAGING)
    assert len(sources) == 3
    assert all(isinstance(s, SourceSpec) for s in sources)

def test_2_correct_source_types():
    sources = build_config_sources("qa-engine.yaml", Environment.STAGING)
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_3_correct_policies():
    sources = build_config_sources("qa-engine.yaml", Environment.STAGING)
    assert sources[0].failure_policy == FailurePolicy.REQUIRED  # YAML
    assert sources[1].failure_policy == FailurePolicy.OPTIONAL  # ENV
    assert sources[2].failure_policy == FailurePolicy.OPTIONAL  # CLI

def test_4_correct_ordering():
    sources = build_config_sources("qa-engine.yaml", Environment.STAGING)
    # Order must be YAML -> ENV -> CLI
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_5_settings_uses_composition_layer(monkeypatch):
    # Mock build_config_sources to ensure Settings delegates to it
    mock_called = {"called": False}
    
    def mock_build(file_path, env, cli_args=None):
        mock_called["called"] = True
        # Return an empty list to prove the mock is used
        return []
        
    monkeypatch.setattr("framework.config.settings.build_standard_pipeline", mock_build)
    
    # We expect a validation error because no sources provide required fields,
    # but we only care that the mock was called.
    with pytest.raises(ValueError, match="Missing required configuration field"):
        Settings.from_config_file("qa-engine.yaml", Environment.STAGING, cli_args=[])
        
    assert mock_called["called"] is True