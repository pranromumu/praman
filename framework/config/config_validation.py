def validate_config(config: object, source_name: str) -> dict:
    """
    Validates that a configuration source returns a dictionary.
    """
    if not isinstance(config, dict):
        raise TypeError(
            f"Configuration source {source_name} must return a dict, "
            f"got {type(config).__name__}"
        )
    return config
