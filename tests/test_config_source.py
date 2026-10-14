import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.source import ConfigSource

def test_config_source_cannot_be_instantiated_directly():
    # Attempting to instantiate the abstract base class should raise a TypeError
    with pytest.raises(TypeError, match="abstract class"):
        ConfigSource()

def test_concrete_subclass_can_be_instantiated():
    # Create a valid subclass that implements the abstract method
    class ValidSource(ConfigSource):
        def get_config(self):
            return {"browser": "firefox"}
            
    source = ValidSource()
    assert isinstance(source, ConfigSource)

def test_concrete_subclass_returns_dict():
    class ValidSource(ConfigSource):
        def get_config(self):
            return {"timeout": 30000, "headless": True}
            
    source = ValidSource()
    config = source.get_config()
    
    assert isinstance(config, dict)
    assert config["timeout"] == 30000
    assert config["headless"] is True

def test_subclass_without_implementation_cannot_be_instantiated():
    # Create an invalid subclass that does NOT implement get_config()
    class InvalidSource(ConfigSource):
        pass
        
    with pytest.raises(TypeError, match="abstract class"):
        InvalidSource()