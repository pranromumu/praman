from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, env_name: str) -> "Environment":
        normalized_name = env_name.lower().strip()
        for env in cls:
            if env.value == normalized_name:
                return env
                
        supported = [e.value for e in cls]
        raise ValueError(
            f"Unsupported environment: '{env_name}'. "
            f"Supported environments are: {supported}"
        )