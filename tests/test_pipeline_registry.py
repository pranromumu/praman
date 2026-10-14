import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.pipeline_registry import PIPELINE_REGISTRY
from framework.config.pipeline_selector import select_pipeline
from framework.config.pipeline_builder import build_standard_pipeline, build_test_pipeline
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource
from framework.config.environment import Environment
from framework.config.resolver import resolve_config

def test_1_standard_is_registered():
    assert "standard" in PIPELINE_REGISTRY
    assert PIPELINE_REGISTRY["standard"] is build_standard_pipeline

def test_2_test_is_registered():
    assert "test" in PIPELINE_REGISTRY
    assert PIPELINE_REGISTRY["test"] is build_test_pipeline

def test_3_selector_uses_registry(monkeypatch):
    # Mock the registry to prove the selector looks up the name in the registry
    # rather than using hard-coded if/elif branches.
    mock_called = {"called": False}
    
    def mock_builder(**kwargs):
        mock_called["called"] = True
        return []
        
    monkeypatch.setitem(PIPELINE_REGISTRY, "mocked_pipeline", mock_builder)
    
    select_pipeline("mocked_pipeline", cli_args=[])
    assert mock_called["called"] is True

def test_4_selector_has_no_hardcoded_pipeline_branches():
    # Read source code to prove no 'if pipeline_name == "standard"' or 'elif' logic exists
    import framework.config.pipeline_selector as selector_module
    source_code = inspect.getsource(selector_module)
    
    assert '== "standard"' not in source_code
    assert '== "test"' not in source_code
    assert 'elif' not in source_code

def test_5_unknown_pipeline_raises_error():
    with pytest.raises(ValueError, match="Unknown pipeline name: 'unknown'"):
        select_pipeline("unknown", cli_args=[])

def test_6_standard_pipeline_still_works():
    sources = select_pipeline("standard", file_path="qa-engine.yaml", env=Environment.STAGING, cli_args=[])
    assert isinstance(sources[0].source, YAMLSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_7_test_pipeline_still_works():
    sources = select_pipeline("test", fake_config={"base_url": "https://test.com"}, cli_args=[])
    assert isinstance(sources[0].source, FakeConfigSource)
    assert isinstance(sources[1].source, EnvSource)
    assert isinstance(sources[2].source, CLISource)

def test_8_resolver_remains_unchanged():
    # Verify the resolver signature hasn't been modified to accept pipeline names or registries
    sig = inspect.signature(resolve_config)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "sources"