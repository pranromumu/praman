import sys
import os
import inspect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from framework.compatibility.versioned_source import VersionedSource
from framework.contracts.normalized_provider import NormalizedConfigProvider

class FakeSource:
    pass

def test_1_stores_source_correctly():
    source = FakeSource()
    vs = VersionedSource(source=source, source_version=1, supported_versions=[1])
    assert vs.source is source

def test_2_stores_source_version_correctly():
    vs = VersionedSource(source=FakeSource(), source_version=2, supported_versions=[2])
    assert vs.source_version == 2

def test_3_stores_supported_versions_correctly():
    vs = VersionedSource(source=FakeSource(), source_version=1, supported_versions=[1, 2, 3])
    assert vs.supported_versions == [1, 2, 3]

def test_4_frozen_true_prevents_mutation():
    vs = VersionedSource(source=FakeSource(), source_version=1, supported_versions=[1])
    with pytest.raises(Exception):
        vs.source_version = 2

def test_5_does_not_depend_on_normalized_provider():
    module = sys.modules['framework.compatibility.versioned_source']
    source_code = inspect.getsource(module)
    assert "NormalizedConfigProvider" not in source_code

def test_6_lives_within_compatibility_boundary():
    file_path = inspect.getfile(VersionedSource)
    # Verify it physically lives in the compatibility folder
    assert "framework" in file_path
    assert "compatibility" in file_path