from typing import Any
from framework.config.pipeline_registry import PIPELINE_REGISTRY
from framework.config.source_spec import SourceSpec

def select_pipeline(pipeline_name: str, **kwargs: Any) -> list[SourceSpec]:
    """
    Selects and builds the appropriate configuration pipeline using the registry.
    """
    builder = PIPELINE_REGISTRY.get(pipeline_name)
    
    if builder is None:
        raise ValueError(
            f"Unknown pipeline name: '{pipeline_name}'. "
            f"Supported pipelines: {list(PIPELINE_REGISTRY.keys())}."
        )
        
    return builder(**kwargs)