from unittest import mock

import pytest

from migration_lambda.verify_migrations import MigrationHashMismatchError, get_atlas_hash_value, verify_migration_hash
from tests.migration_lambda.util import build_cfn_event


def test__get_atlas_hash_value__returns_hash_value():
    hash_value = get_atlas_hash_value()
    assert len(hash_value) == 44
    assert hash_value[-1] == "="


@mock.patch("migration_lambda.verify_migrations.get_atlas_hash_value")
def test__verify_migration_hash__raises_exception__when_hashes_do_not_match(mock_get_atlas_hash_value):
    event = build_cfn_event("Create")
    mock_get_atlas_hash_value.return_value = "DifferentValue"
    with pytest.raises(MigrationHashMismatchError):
        verify_migration_hash(event)


@mock.patch("migration_lambda.verify_migrations.get_atlas_hash_value")
def test__verify_migration_hash__does_not_raise_exception__when_hashes_match(mock_get_atlas_hash_value):
    event = build_cfn_event("Create")
    mock_get_atlas_hash_value.return_value = event["ResourceProperties"]["MigrationHash"]
    verify_migration_hash(event)
