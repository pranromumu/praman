
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True)
class ApiSettings:
    """Configuration for API request behavior."""

    HEADERS: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self):
        """Validate and protect API headers after initialization."""

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

        allowed_fields = {"headers"}
        unknown_fields = set(config) - allowed_fields

        if unknown_fields:
            raise ValueError(
                "Unexpected API configuration field(s): "
                f"{sorted(unknown_fields, key=str)}"
            )

        headers = config.get("headers", {})

        return cls(HEADERS=headers)
