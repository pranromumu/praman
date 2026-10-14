import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.policies.version_selection import (
    VersionSelectionPolicy,
    BaseVersionSelectionPolicy,
    HighestVersionPolicy,
    LowestVersionPolicy
)

class TestPolicySelection:
    @pytest.fixture
    def highest_policy(self):
        return HighestVersionPolicy()

    @pytest.fixture
    def lowest_policy(self):
        return LowestVersionPolicy()

    def test_highest_version_selected(self, highest_policy):
        result = highest_policy.select_version([1, 2, 3], [2, 3, 4])
        assert result == 3

    def test_lowest_version_selected(self, lowest_policy):
        result = lowest_policy.select_version([1, 2, 3], [2, 3, 4])
        assert result == 2

    def test_duplicates_are_ignored(self, highest_policy, lowest_policy):
        client = [1, 2, 2, 3]
        praman = [2, 3, 3, 4]
        
        assert highest_policy.select_version(client, praman) == 3
        assert lowest_policy.select_version(client, praman) == 2


class TestPolicyValidation:
    @pytest.fixture
    def policies(self):
        return [HighestVersionPolicy(), LowestVersionPolicy()]

    def test_empty_client_list_fails(self, policies):
        for policy in policies:
            with pytest.raises(ValueError, match="client_supported_versions must be a non-empty list"):
                policy.select_version([], [1, 2])

    def test_empty_praman_list_fails(self, policies):
        for policy in policies:
            with pytest.raises(ValueError, match="praman_supported_versions must be a non-empty list"):
                policy.select_version([1, 2], [])

    def test_string_in_list_fails(self, policies):
        for policy in policies:
            with pytest.raises(ValueError, match="Invalid version type"):
                policy.select_version([1, "2", 3], [2, 3])

    def test_boolean_in_list_fails(self, policies):
        for policy in policies:
            with pytest.raises(ValueError, match="Invalid version type"):
                policy.select_version([1, True, 3], [2, 3])

    def test_no_mutual_versions_fails(self, policies):
        for policy in policies:
            with pytest.raises(ValueError, match="No mutually supported contract version"):
                policy.select_version([1, 2], [3, 4])


class TestPolicyAbstraction:
    def test_cannot_instantiate_abstract_policy(self):
        with pytest.raises(TypeError):
            VersionSelectionPolicy()

    def test_cannot_instantiate_base_policy(self):
        with pytest.raises(TypeError):
            BaseVersionSelectionPolicy()

    def test_concrete_policies_inherit_from_base(self):
        assert issubclass(HighestVersionPolicy, BaseVersionSelectionPolicy)
        assert issubclass(LowestVersionPolicy, BaseVersionSelectionPolicy)
        assert issubclass(HighestVersionPolicy, VersionSelectionPolicy)