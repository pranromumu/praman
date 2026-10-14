from framework.contracts.config_source_v1 import ConfigSourceV1

class LegacyV1Source(ConfigSourceV1):
    """
    Represents an old client implementation using the V1 contract.
    """
    def get_config(self) -> dict:
        return {
            "browser": "chromium"
        }