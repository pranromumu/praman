import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.config_loader import load_config

def test_load_valid_config():
    # This assumes qa-engine.yaml is in the root of the project
    # when pytest runs from the root directory.
    config = load_config("qa-engine.yaml")
    
    # Verify it returned a dictionary
    assert isinstance(config, dict)
    
    # Verify it parsed the environments correctly
    assert "environments" in config
    assert "staging" in config["environments"]
    assert config["environments"]["staging"]["base_url"] == "https://staging.client.com"

def test_missing_config_raises_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_config("fake-missing-file.yaml")
        
    # Verify the error message is clear and helpful for the client
    assert "Praman configuration file not found" in str(exc_info.value)