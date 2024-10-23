# This script should never be run or imported directly, and is only used by Atlas
import sys
from pathlib import Path

from atlas_provider_sqlalchemy.ddl import print_ddl

SOURCE_ROOT_DIR = Path(__file__).resolve().parents[0] / "src"

# Add the source root of the project to the path so we can import the models
# Insert at the beginning of the path to ensure we do not import the models from the installed version of the package
sys.path.insert(0, str(SOURCE_ROOT_DIR))

from db.models import Address, User

print_ddl("postgresql", [User, Address])
