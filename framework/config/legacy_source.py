class LegacySource:
    """
    Represents an old client implementation.
    It has its own API and does NOT inherit from ConfigSourceV2.
    """
    def get_config(self) -> dict:
        return {
            "browser": "chromium"
        }