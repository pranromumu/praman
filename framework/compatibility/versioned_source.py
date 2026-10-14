from dataclasses import dataclass
from typing import Any, List

@dataclass(frozen=True)
class VersionedSource:
    """
    Descriptor for an incoming versioned configuration source.
    
    Used by the compatibility negotiation boundary to group client-side
    source metadata into a single, cohesive object.
    """
    source: Any
    source_version: int
    supported_versions: List[int]