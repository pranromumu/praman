import yaml
from pathlib import Path

def load_config(file_path: str = "qa-engine.yaml") -> dict:
    """
    Loads and parses the client-owned qa-engine.yaml configuration file.
    Uses yaml.safe_load() to prevent arbitrary code execution.
    """
    config_path = Path(file_path)
    
    # 1. Fail fast if the configuration file does not exist
    if not config_path.exists():
        raise FileNotFoundError(
            f"Praman configuration file not found: '{file_path}'. "
            f"Please ensure 'qa-engine.yaml' exists in the root directory."
        )
        
    # 2. Read and safely parse the YAML file
    with config_path.open('r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file '{file_path}': {e}")
            
        # 3. Fail fast if the file exists but is empty
    if data is None:
        raise ValueError(f"Configuration file '{file_path}' is empty.")

    # 4. Ensure the YAML root is a dictionary
    if not isinstance(data, dict):
        raise ValueError(
            f"Configuration file '{file_path}' must contain a dictionary "
            f"at the YAML root, but got {type(data).__name__}."
        )

    return data