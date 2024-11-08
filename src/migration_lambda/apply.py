import subprocess
from dataclasses import dataclass
from urllib.parse import quote_plus

from migration_lambda.dirs import MIGRATIONS_DIR


@dataclass
class DBConfig:
    host: str
    port: int
    name: str
    user: str
    password: str


def apply_migrations(db_config: DBConfig) -> subprocess.CompletedProcess[str]:
    """
    Use Atlas to apply pending migrations, return the subprocess call result
    """
    db_url = f"postgresql://{db_config.user}:{quote_plus(db_config.password)}@{quote_plus(db_config.host)}:{db_config.port}/{db_config.name}"
    # Verify directory exists
    assert MIGRATIONS_DIR.exists(), f"Migration directory not found: {MIGRATIONS_DIR}"

    # This does not need to access atlas.hcl to run
    result = subprocess.run(
        ["atlas", "migrate", "apply", "-u", db_url, "--dir", f"file://{MIGRATIONS_DIR}"],
        capture_output=True,
        text=True,
    )
    return result
