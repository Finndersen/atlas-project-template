import subprocess

import pytest

from migration_lambda.dirs import SOURCE_ROOT_DIR

PROJECT_ROOT_DIR = SOURCE_ROOT_DIR.parents[0]


def test__load_models__prints_sql_for_all_tables():
    result = subprocess.run(["python", "scripts/load_models.py"], cwd=PROJECT_ROOT_DIR, capture_output=True, text=True)
    if result.returncode:
        pytest.fail(f"Error when running load_models.py: {result.stderr}")
    create_tables_sql = result.stdout
    assert "CREATE TABLE users" in create_tables_sql
    assert "CREATE TABLE addresses" in create_tables_sql
