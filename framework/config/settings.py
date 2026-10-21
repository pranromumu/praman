
from dataclasses import dataclass

from framework.config.environment import Environment
from framework.config.resolver import resolve_config
from framework.config.pipeline_builder import build_standard_pipeline
from framework.compatibility.policies.policy_name_provider import PolicyNameProvider
from framework.compatibility.composition import build_version_policy_factory


@dataclass(frozen=True)
class Settings:
    """
    Central configuration for the Praman QA Engine.
    """

    BASE_URL: str = ""
    BROWSER: str = "chromium"
    HEADLESS: bool = True
    TIMEOUT: int = 30000
    VERSION_POLICY: str = "highest"

    def get_validation_errors(
        self,
        policy_name_provider: PolicyNameProvider | None = None,
    ) -> list[str]:
        errors = []

        if not isinstance(self.BASE_URL, str):
            errors.append(
                f"BASE_URL must be a string, but got "
                f"{type(self.BASE_URL).__name__}."
            )
        elif not self.BASE_URL.strip():
            errors.append("BASE_URL cannot be empty.")

        supported_browsers = ["chromium", "firefox", "webkit"]

        if not isinstance(self.BROWSER, str):
            errors.append(
                f"BROWSER must be a string, but got "
                f"{type(self.BROWSER).__name__}."
            )
        elif self.BROWSER not in supported_browsers:
            errors.append(
                f"BROWSER must be one of {supported_browsers}, "
                f"but got '{self.BROWSER}'."
            )

        if not isinstance(self.HEADLESS, bool):
            errors.append(
                "HEADLESS must be a boolean (True/False), "
                f"but got {type(self.HEADLESS).__name__}."
            )

        if (
            not isinstance(self.TIMEOUT, int)
            or isinstance(self.TIMEOUT, bool)
            or self.TIMEOUT <= 0
        ):
            errors.append(
                f"TIMEOUT must be an integer greater than 0, "
                f"but got {self.TIMEOUT}."
            )

        if (
            not isinstance(self.VERSION_POLICY, str)
            or not self.VERSION_POLICY.strip()
        ):
            errors.append("VERSION_POLICY must be a non-empty string.")
        elif policy_name_provider is not None:
            supported_names = (
                policy_name_provider.get_supported_policy_names()
            )
            if self.VERSION_POLICY not in supported_names:
                errors.append(
                    f"VERSION_POLICY must be one of {supported_names}, "
                    f"but got '{self.VERSION_POLICY}'."
                )

        return errors

    def validate(
        self,
        policy_name_provider: PolicyNameProvider | None = None,
    ) -> None:
        if policy_name_provider is None:
            policy_name_provider = build_version_policy_factory()

        errors = self.get_validation_errors(policy_name_provider)

        if errors:
            error_message = "\n".join(f"- {error}" for error in errors)
            raise ValueError(
                f"Configuration validation failed:\n{error_message}"
            )

    @classmethod
    def from_config(
        cls,
        config: dict,
        policy_name_provider: PolicyNameProvider | None = None,
    ) -> "Settings":
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary.")

        if policy_name_provider is None:
            policy_name_provider = build_version_policy_factory()

        errors = []

        allowed_fields = {
            "base_url",
            "headless",
            "timeout",
            "browser",
            "version_policy",
        }
        provided_fields = set(config.keys())

        unknown_fields = provided_fields - allowed_fields

        for field in sorted(unknown_fields):
            message = f"Unexpected configuration field: '{field}'"
            if field == "baseurl":
                message += " Did you mean 'base_url'?"
            errors.append(message)

        required_fields = {"base_url", "headless", "timeout"}
        missing_fields = required_fields - provided_fields

        if missing_fields:
            errors.append(
                "Missing required configuration field(s): "
                f"{sorted(missing_fields)}"
            )

            raise ValueError(
                "Configuration validation failed:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

        mapped_config = {
            "BASE_URL": config["base_url"],
            "HEADLESS": config["headless"],
            "TIMEOUT": config["timeout"],
        }

        if "browser" in config:
            mapped_config["BROWSER"] = config["browser"]

        if "version_policy" in config:
            mapped_config["VERSION_POLICY"] = config["version_policy"]

        settings = cls(**mapped_config)

        value_errors = settings.get_validation_errors(
            policy_name_provider
        )
        errors.extend(value_errors)

        if errors:
            raise ValueError(
                "Configuration validation failed:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

        return settings

    @classmethod
    def from_config_file(
        cls,
        file_path: str,
        env: Environment,
        cli_args=None,
        policy_name_provider: PolicyNameProvider | None = None,
    ) -> "Settings":
        sources = build_standard_pipeline(
            file_path=file_path,
            env=env,
            cli_args=cli_args,
        )
        merged_config = resolve_config(sources)

        return cls.from_config(
            merged_config,
            policy_name_provider=policy_name_provider,
        )
