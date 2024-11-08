from pathlib import Path

SOURCE_ROOT_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = SOURCE_ROOT_DIR / "db" / "migrations"
