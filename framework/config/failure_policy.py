from enum import Enum

class FailurePolicy(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"