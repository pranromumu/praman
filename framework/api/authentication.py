
import os

from framework.config.api_settings import ApiSettings


def build_api_headers(settings: ApiSettings) -> dict[str, str]:
    """Build API request headers, resolving configured authentication safely."""

    if not isinstance(settings, ApiSettings):
        raise ValueError("API settings must be an ApiSettings instance.")

    headers = dict(settings.HEADERS)

    authentication = settings.AUTHENTICATION

    if authentication is None:
        return headers

    if authentication.TYPE == "bearer":
        token = os.environ.get(authentication.TOKEN_ENV)

        if token is None:
            raise ValueError(
                "API authentication token environment variable "
                f"'{authentication.TOKEN_ENV}' is not set."
            )

        if "\r" in token or "\n" in token:
            raise ValueError(
                "API authentication token cannot contain newline characters."
            )

        token = token.strip()

        if not token:
            raise ValueError(
                "API authentication token cannot be empty."
            )

        headers["Authorization"] = f"Bearer {token}"
        return headers

    # ApiAuthenticationSettings currently validates supported types.
    # This guard protects against unexpected settings implementations.
    raise ValueError("Unsupported API authentication type.")
