import pytest
from framework.compatibility.policies.policy_name_provider import (
    PolicyNameProvider,
)

class TestPolicyNameProvider(PolicyNameProvider):
    def get_supported_policy_names(self) -> list[str]:
        return ["highest", "lowest"]

def test_provider_contract_cannot_be_instantiated():
    with pytest.raises(TypeError):
        PolicyNameProvider()

def test_concrete_provider_returns_policy_names():
    provider = TestPolicyNameProvider()
    assert provider.get_supported_policy_names() == [
        "highest",
        "lowest",
    ]