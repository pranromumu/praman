import copy
import logging
from collections.abc import Iterable

from framework.contracts.config_source import ConfigSource
from framework.config.config_validation import validate_config
from framework.config.failure_policy import FailurePolicy
from framework.config.source_spec import SourceSpec

logger = logging.getLogger(__name__)


def resolve_config(sources: Iterable[SourceSpec]) -> dict:
    """
    Merges configuration from an iterable of SourceSpec objects.

    Required sources propagate failures.
    Optional sources are skipped when fetching, validating, or merging
    their configuration fails.
    """
    merged_config = {}

    for spec in sources:
        try:
            config = spec.source.get_config()
            config = validate_config(
                config,
                spec.source.__class__.__name__,
            )
            config = copy.deepcopy(config)
            merged_config = {**merged_config, **config}

        except Exception as error:
            if spec.failure_policy == FailurePolicy.REQUIRED:
                raise

            logger.warning(
                "Optional configuration source %s failed: %s",
                spec.source.__class__.__name__,
                error,
            )
            continue

    return merged_config
