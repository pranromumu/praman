import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_policy_factory import VersionPolicyFactory
from framework.compatibility.policies.version_selection import (
    HighestVersionPolicy, 
    LowestVersionPolicy,
    VersionSelectionPolicy,
    BaseVersionSelectionPolicy
)
from framework.compatibility.composition import build_version_policy_factory
from framework.compatibility.policies.policy_name_provider import PolicyNameProvider # NEW

# A custom policy for Test 8
class CustomPolicy(BaseVersionSelectionPolicy):
    def do_select_version(self, mutual_versions):
        # Using min() ensures deterministic behavior instead of relying on set iteration order
        return min(mutual_versions)

@pytest.fixture
def factory():
    return VersionPolicyFactory()

def test_1_register_and_create_highest(factory):
    factory.register_policy("highest", HighestVersionPolicy)
    policy = factory.create_policy("highest")
    assert isinstance(policy, HighestVersionPolicy)

def test_2_register_and_create_lowest(factory):
    factory.register_policy("lowest", LowestVersionPolicy)
    policy = factory.create_policy("lowest")
    assert isinstance(policy, LowestVersionPolicy)

def test_3_new_instance_each_call(factory):
    factory.register_policy("highest", HighestVersionPolicy)
    p1 = factory.create_policy("highest")
    p2 = factory.create_policy("highest")
    assert p1 is not p2

def test_4_unknown_policy_name_rejected(factory):
    with pytest.raises(ValueError, match="Unknown policy name"):
        factory.create_policy("unknown")

def test_5_empty_name_rejected(factory):
    with pytest.raises(ValueError, match="non-empty string"):
        factory.register_policy("", HighestVersionPolicy)
    with pytest.raises(ValueError, match="non-empty string"):
        factory.register_policy("   ", HighestVersionPolicy)

def test_6_invalid_or_abstract_class_rejected(factory):
    # Not a class
    with pytest.raises(ValueError, match="must be a type"):
        factory.register_policy("invalid", "not_a_class")
        
    # Abstract base class
    with pytest.raises(ValueError, match="abstract policy class"):
        factory.register_policy("abstract", VersionSelectionPolicy)
        
    # Intermediate abstract class
    with pytest.raises(ValueError, match="abstract policy class"):
        factory.register_policy("abstract_base", BaseVersionSelectionPolicy)

def test_7_duplicate_registration_rejected(factory):
    factory.register_policy("highest", HighestVersionPolicy)
    with pytest.raises(ValueError, match="already registered"):
        factory.register_policy("highest", LowestVersionPolicy)

def test_8_custom_policy_without_factory_modification(factory):
    # Proves OCP: We can add new policies without changing VersionPolicyFactory code
    factory.register_policy("custom", CustomPolicy)
    policy = factory.create_policy("custom")
    assert isinstance(policy, CustomPolicy)
    # Verify it actually works
    assert policy.select_version([1, 2], [2, 3]) == 2

# --- Step 83 Task 1 & 3 Tests ---

def test_9_get_supported_policy_names():
    # Using the production factory builder which registers "highest" and "lowest"
    factory = build_version_policy_factory()
    names = factory.get_supported_policy_names()
    assert names == ["highest", "lowest"]

def test_10_supported_policy_names_returns_independent_list():
    factory = build_version_policy_factory()
    names = factory.get_supported_policy_names()
    
    # Mutate the returned list
    names.append("middle")
    names.remove("highest")
    
    # Verify the factory's internal state is unchanged
    assert factory.get_supported_policy_names() == ["highest", "lowest"]

#Task 3 Tests
def test_11_factory_is_policy_name_provider():
    factory = build_version_policy_factory()
    assert isinstance(factory, PolicyNameProvider)
    assert factory.get_supported_policy_names() == ["highest", "lowest"]


def test_12_factory_registers_and_creates_additional_policy_name():
    factory = VersionPolicyFactory()
    factory.register_policy("middle", HighestVersionPolicy)
    assert factory.get_supported_policy_names() == ["middle"]
    policy = factory.create_policy("middle")
    assert isinstance(policy, HighestVersionPolicy)