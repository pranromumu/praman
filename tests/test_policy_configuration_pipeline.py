import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.config.composition import resolve_praman_config
from framework.compatibility.composition import build_compatibility_registry, build_version_policy_factory
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.v1_to_v2 import V1ToV2Adapter
from framework.config.legacy_v1_source import LegacyV1Source
from framework.contracts.config_source_v2 import ConfigSourceV2
from framework.compatibility.versioned_source import VersionedSource

@pytest.fixture
def registry():
    # Register a (1, 2) and a (1, 3) adapter to test highest vs lowest selection
    reg = CompatibilityRegistry()
    reg.register_adapter(1, 2, V1ToV2Adapter)
    # Create a fake adapter for (1, 3) just to prove highest could find it if it wanted to
    class FakeV3Adapter(V1ToV2Adapter): pass
    reg.register_adapter(1, 3, FakeV3Adapter)
    return reg

@pytest.fixture
def factory():
    return build_version_policy_factory()

def test_1_default_policy_is_highest(registry, factory):
    # Client: [1, 2, 3], Praman: [2, 3]. Mutual: {2, 3}. Highest selects 3.
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2, 3])
    result = resolve_praman_config(
        versioned_source=vs,
        praman_supported_versions=[2, 3],
        environment="prod",
        registry=registry,
        policy_factory=factory,
        version_policy_name="highest" # Explicit default
    )
    assert result["browser"] == "chromium"

def test_2_lowest_policy_from_config(registry, factory):
    # Client: [1, 2, 3], Praman: [2, 3]. Mutual: {2, 3}. Lowest selects 2.
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2, 3])
    result = resolve_praman_config(
        versioned_source=vs,
        praman_supported_versions=[2, 3],
        environment="prod",
        registry=registry,
        policy_factory=factory,
        version_policy_name="lowest"
    )
    assert result["browser"] == "chromium"

def test_3_invalid_policy_name_rejected(registry, factory):
    vs = VersionedSource(source=LegacyV1Source(), source_version=1, supported_versions=[1, 2])
    with pytest.raises(ValueError, match="Unknown policy name: 'middle'"):
        resolve_praman_config(
            versioned_source=vs,
            praman_supported_versions=[2],
            environment="prod",
            registry=registry,
            policy_factory=factory,
            version_policy_name="middle"
        )

def test_4_settings_load_version_policy():
    from framework.config.settings import Settings
    
    # Default is highest
    config = {"base_url": "http://test.com", "headless": True, "timeout": 1000}
    settings = Settings.from_config(config)
    assert settings.VERSION_POLICY == "highest"
    
    # Can be overridden
    config["version_policy"] = "lowest"
    settings = Settings.from_config(config)
    assert settings.VERSION_POLICY == "lowest"