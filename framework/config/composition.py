from typing import List, Any, Optional
from framework.compatibility.registry import CompatibilityRegistry
from framework.compatibility.negotiation import negotiate_contract
from framework.compatibility.normalization import normalize_v2_source
from framework.compatibility.versioned_source import VersionedSource
from framework.compatibility.policies.version_policy_factory import VersionPolicyFactory
from framework.compatibility.policies.version_selection import VersionSelectionPolicy
from framework.config.resolver import resolve_config
from framework.config.source_spec import SourceSpec
from framework.config.failure_policy import FailurePolicy
from framework.config.environment import Environment
from framework.config.yaml_source import YAMLSource
from framework.config.env_source import EnvSource
from framework.config.cli_source import CLISource

# --- Step 18: Standard Pipeline Composition ---

def build_config_sources(file_path: str, env: Environment, cli_args=None) -> list[SourceSpec]:
    yaml_source = YAMLSource(file_path, env)
    env_source = EnvSource()
    cli_source = CLISource(args=cli_args)
    return [
        SourceSpec(source=yaml_source, failure_policy=FailurePolicy.REQUIRED),
        SourceSpec(source=env_source, failure_policy=FailurePolicy.OPTIONAL),
        SourceSpec(source=cli_source, failure_policy=FailurePolicy.OPTIONAL),
    ]

# --- Step 80: Versioned Pipeline Composition Root ---

def resolve_praman_config(
    versioned_source: VersionedSource,
    praman_supported_versions: List[int],
    environment: str,
    registry: CompatibilityRegistry,
    policy_factory: VersionPolicyFactory,
    version_policy_name: str = "highest",
    failure_policy: FailurePolicy = FailurePolicy.REQUIRED
) -> dict:
    """
    Orchestrates the compatibility, normalization, and resolution pipeline.
    """
    # 1. Create policy instance from string configuration
    # The factory will raise ValueError if the name is unknown.
    version_policy = policy_factory.create_policy(version_policy_name)
    
    # 2. Negotiate contract version and adapt
    adapted_source = negotiate_contract(
        versioned_source=versioned_source,
        praman_supported_versions=praman_supported_versions,
        registry=registry,
        version_policy=version_policy
    )
    
    # 3. Normalize to parameterless provider
    normalized_provider = normalize_v2_source(
        source=adapted_source,
        environment=environment
    )
    
    # 4. Wrap in SourceSpec
    specs = [SourceSpec(source=normalized_provider, failure_policy=failure_policy)]
    
    # 5. Resolve
    return resolve_config(specs)