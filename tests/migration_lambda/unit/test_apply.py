from pathlib import Path
from unittest import mock

from migration_lambda.apply import DBConfig, apply_migrations

test_db_config = DBConfig(
    host="database.rds.aws.com", port=5432, name="MyDatabase", user="masterUser", password="mypassword"
)


@mock.patch("subprocess.run")
def test__apply_migrations__calls_subprocess_run__with_correct_args(mock_subprocess_run):
    mock_subprocess_run.return_value = mock.MagicMock(returncode=0, stdout="Success")
    result = apply_migrations(test_db_config)

    db_url = "postgresql://masterUser:mypassword@database.rds.aws.com:5432/MyDatabase"
    migration_dir = Path(__file__).resolve().parents[3] / "src" / "db" / "migrations"
    mock_subprocess_run.assert_called_with(
        ["atlas", "migrate", "apply", "-u", db_url, "--dir", f"file://{migration_dir}"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == "Success"
