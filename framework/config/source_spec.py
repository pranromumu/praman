from dataclasses import dataclass
from framework.contracts.normalized_provider import NormalizedConfigProvider
from framework.config.failure_policy import FailurePolicy

@dataclass
class SourceSpec:
    """
    Registration object for a configuration source.
    """
    source: NormalizedConfigProvider
    failure_policy: FailurePolicy