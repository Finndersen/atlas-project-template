from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from migration_lambda.dirs import MIRATIONS_DIR


class MigrationHashMismatchError(Exception):
    pass


def get_atlas_hash_value() -> str:
    """
    Get the header hash value from the atlas.sum file
    """
    atlas_sum_file = MIRATIONS_DIR / "atlas.sum"
    with atlas_sum_file.open("rt") as f:
        return f.readline()[3:].strip()


def verify_migration_hash(event: APIGatewayProxyEvent) -> None:
    """
    Verify that the MigrationHash parameter of the MigrationTrigger CloudFormation custom resource
    matches the hash value from the atlas.sum file
    """
    cr_migration_hash = event["ResourceProperties"]["MigrationHash"]
    atlas_hash = get_atlas_hash_value()
    if cr_migration_hash != atlas_hash:
        raise MigrationHashMismatchError(
            f"Provided MigrationHash '{cr_migration_hash}' does not match hash of migration files: '{atlas_hash}'"
        )
