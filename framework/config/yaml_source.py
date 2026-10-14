import yaml
from pathlib import Path
from framework.contracts.config_source import ConfigSource
from framework.config.environment import Environment


class YAMLSource(ConfigSource):
    """
    Configuration source that reads from a YAML file.
    
    Parses the YAML, selects the requested environment,
    and returns a flat configuration dictionary.
    
    Does NOT perform business validation (e.g., timeout > 0, browser supported).
    """
    
    def __init__(self, file_path: str, env: Environment):
        self._file_path = file_path
        self._env = env
    
    def get_config(self) -> dict:
        """Loads the YAML file and returns the selected environment's configuration."""
        config_path = Path(self._file_path)
        
        # 1. Fail fast if the file doesn't exist
        if not config_path.exists():
            raise FileNotFoundError(
                f"Praman configuration file not found: '{self._file_path}'. "
                f"Please ensure 'qa-engine.yaml' exists in the root directory."
            )
        
        # 2. Read and safely parse the YAML file
        with config_path.open('r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file '{self._file_path}': {e}")
        
        # 3. Fail fast if the file is empty
        if data is None:
            raise ValueError(f"Configuration file '{self._file_path}' is empty.")
        
        # 4. Structural validation: 'environments' key must exist
        if "environments" not in data or not isinstance(data["environments"], dict):
            raise ValueError(
                f"Missing or invalid 'environments' key in '{self._file_path}'. "
                f"Expected a dictionary of environments."
            )
        
        environments = data["environments"]
        env_name = self._env.value
        env_config = environments.get(env_name)
        
        # 5. Requested environment must exist
        if env_config is None:
            raise ValueError(
                f"Configuration for environment '{env_name}' not found in '{self._file_path}'."
            )
        
        # 6. Environment configuration must be a dictionary
        if not isinstance(env_config, dict):
            raise ValueError(
                f"Configuration for environment '{env_name}' must be a dictionary, "
                f"but got {type(env_config).__name__}."
            )
        
        # 7. Return the flat configuration dictionary (NO business validation!)
        return env_config