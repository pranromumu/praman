from framework.config.pipeline_builder import (
    build_standard_pipeline, 
    build_test_pipeline,
    build_ci_pipeline
)

PIPELINE_REGISTRY = {
    "standard": build_standard_pipeline,
    "test": build_test_pipeline,
    "ci": build_ci_pipeline,
}