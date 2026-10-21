
from enum import Enum


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, env_name: str) -> "Environment":
        if not isinstance(env_name, str):
            raise ValueError("Environment name must be a string")

        normalized_name = env_name.lower().strip()

        if not normalized_name:
            raise ValueError("Environment name must not be empty")

        for env in cls:
            if env.value == normalized_name:
                return env

        supported = [env.value for env in cls]
        raise ValueError(
            f"Unsupported environment: '{env_name}'. "
            f"Supported environments are: {supported}"
        )
