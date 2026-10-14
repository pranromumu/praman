from framework.config.environment import Environment
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.contracts.config_source import ConfigSource
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource
from framework.config.fake_source import FakeConfigSource

def build_standard_pipeline(file_path: str, env: Environment, cli_args=None) -> list[SourceSpec]:
    yaml_source = YAMLSource(file_path, env)
    env_source = EnvSource()
    cli_source = CLISource(args=cli_args)
    return [
        SourceSpec(source=yaml_source, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=cli_source, failure_policy=FailurePolicy.OPTIONAL),
    ]

def build_test_pipeline(fake_config: dict, cli_args=None) -> list[SourceSpec]:
    fake_source = FakeConfigSource(fake_config)
    env_source = EnvSource()
    cli_source = CLISource(args=cli_args)
    return [
        SourceSpec(source=fake_source, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=cli_source, failure_policy=FailurePolicy.OPTIONAL),
    ]

def build_ci_pipeline(
    yaml_source: ConfigSource,
    env_source: ConfigSource,
    github_source: ConfigSource,
    cli_source: ConfigSource = None
) -> list[SourceSpec]:
    """
    Constructs a CI pipeline using Dependency Injection.
    Sources are passed in; this builder does NOT instantiate them.
    """
    specs = [
        SourceSpec(source=yaml_source, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=github_source, failure_policy=FailurePolicy.REQUIRED),
    ]
    
    if cli_source is not None:
        specs.append(
            SourceSpec(source=cli_source, failure_policy=FailurePolicy.OPTIONAL)
        )
        
    return specs