
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True)
class ApiAuthenticationSettings:
    """Configuration for API authentication."""

    TYPE: str
    TOKEN_ENV: str

    def __post_init__(self):
        """Validate authentication configuration."""

        if not isinstance(self.TYPE, str):
            raise ValueError("Authentication type must be a string.")

        auth_type = self.TYPE.strip().lower()

        if auth_type != "bearer":
            raise ValueError(
                f"Unsupported authentication type: '{self.TYPE}'."
            )

        if not isinstance(self.TOKEN_ENV, str) or not self.TOKEN_ENV.strip():
            raise ValueError(
                "Authentication token_env must be a non-empty string."
            )

        token_env = self.TOKEN_ENV.strip()

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token_env):
            raise ValueError(
                "Authentication token_env must be a valid environment "
                "variable name."
            )

        object.__setattr__(self, "TYPE", auth_type)
        object.__setattr__(self, "TOKEN_ENV", token_env)

    @classmethod
    def from_config(
        cls,
        config: dict,
    ) -> "ApiAuthenticationSettings":
        """Build authentication settings from configuration."""

        if not isinstance(config, dict):
            raise ValueError(
                "API authentication configuration must be a dictionary."
            )

        allowed_fields = {"type", "token_env"}
        unknown_fields = set(config) - allowed_fields

        if unknown_fields:
            raise ValueError(
                "Unexpected API authentication field(s): "
                f"{sorted(unknown_fields, key=str)}"
            )

        if "type" not in config:
            raise ValueError(
                "API authentication requires a 'type' field."
            )

        if "token_env" not in config:
            raise ValueError(
                "API authentication requires a 'token_env' field."
            )

        return cls(
            TYPE=config["type"],
            TOKEN_ENV=config["token_env"],
        )


@dataclass(frozen=True)
class ApiSettings:
    """Configuration for API request behavior."""

    HEADERS: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )

    AUTHENTICATION: ApiAuthenticationSettings | None = None

    def __post_init__(self):
        """Validate and protect API settings after initialization."""

        if not isinstance(self.HEADERS, Mapping):
            raise ValueError("API headers must be a dictionary.")

        validated_headers = {}
        seen_names = set()

        for name, value in self.HEADERS.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "API header names must be non-empty strings."
                )

            if not isinstance(value, str):
                raise ValueError(
                    f"API header '{name}' must have a string value."
                )

            if "\r" in name or "\n" in name:
                raise ValueError(
                    f"API header '{name}' cannot contain newline characters."
                )

            if "\r" in value or "\n" in value:
                raise ValueError(
                    f"API header '{name}' cannot contain newline characters."
                )

            normalized_name = name.casefold()

            if normalized_name in seen_names:
                raise ValueError(
                    f"Duplicate API header name (case-insensitive): '{name}'."
                )

            seen_names.add(normalized_name)
            validated_headers[name] = value

        if (
            self.AUTHENTICATION is not None
            and not isinstance(
                self.AUTHENTICATION,
                ApiAuthenticationSettings,
            )
        ):
            raise ValueError(
                "API authentication must be an "
                "ApiAuthenticationSettings instance or None."
            )

        if (
            self.AUTHENTICATION is not None
            and "authorization" in seen_names
        ):
            raise ValueError(
                "The Authorization header cannot be configured directly "
                "when API authentication is enabled."
            )

        object.__setattr__(
            self,
            "HEADERS",
            MappingProxyType(validated_headers),
        )

    @classmethod
    def from_config(cls, config: dict | None = None) -> "ApiSettings":
        """Build API settings from a configuration dictionary."""

        if config is None:
            return cls()

        if not isinstance(config, dict):
            raise ValueError("API configuration must be a dictionary.")

        allowed_fields = {"headers", "authentication"}
        unknown_fields = set(config) - allowed_fields

        if unknown_fields:
            raise ValueError(
                "Unexpected API configuration field(s): "
                f"{sorted(unknown_fields, key=str)}"
            )

        headers = config.get("headers", {})

        authentication_config = config.get("authentication")
        authentication = (
            ApiAuthenticationSettings.from_config(authentication_config)
            if authentication_config is not None
            else None
        )

        return cls(
            HEADERS=headers,
            AUTHENTICATION=authentication,
        )
