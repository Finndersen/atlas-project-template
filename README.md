# Atlas Project Template
A project template for managing relational database schema migrations using the [Atlas](https://atlasgo.io/) tool. Contains a collection of scripts and configurations which make the database schema management process simple, safe and automated. 

Involves an implementation of a Python service running on AWS with a PostgreSQL database, but can be adapted to other contexts.

Uses the Atlas [versioned workflow](https://atlasgo.io/versioned/intro) for migrations, and only free features (no Atlas Cloud).

Intended for use on a Mac or Linux development machine.

## Features
 
* `create-migrations` command for generating migration files from changes to DB schema
* `check-migrations` command for validating schema & migration state & integrity, and showing migration-related warnings (can be used as a pre-commit hook and in CI)
* AWS Lambda-backed custom resource for applying migrations upon CloudFormation stack deployment (With a custom parameter that causes the CR to only be triggered when migration state changes, and a Lambda Layer to contain the Atlas binary)
* Automatically installs Atlas and a docker runtime for Mac machines ([colima](https://github.com/abiosoft/colima))

## Installation

Clone this repository, adapt it to your existing project if required.

Run `make install` to install project dependencies.

## Usage
### Configure Database Schema Source
This template comes with an example configuration using SQLAlchemy as a DB schema source. Check the [Atlas docs](https://atlasgo.io/guides) for how to update the `atlas.hcl` configuration file to use a different schema source.

### Create Migrations
Delete the existing files in the `src/db/migrations/` directory, then run `make create-migrations` from the project root to create initial migration and hash files. 

The `MigrationHash` property of the AWS Custom Resource will be automatically updated to the new migration hash value, so that it will be considered updated and trigger the Lambda to run migrations when deployed. 

### Validate Migration files
Running `make check-migrations` will:
* Verify that the `MigrationHash` property of the AWS Custom Resource is set appropriately
* Verify hash integrity of migration files
* Exit early if there are no changes to DB schema or migrations
* Verify that DB schema and migrations are in sync (this involves running the migrations against a temporary database, which will raise any SQL semantic issues)
* Run [Atlas linting](https://atlasgo.io/versioned/lint) which generates warnings for common migration issues

The `make lint` command will run `check-migrations` along with other project linting and type checking.
This command can be added to a Git pre-commit hook, and should be used in your automated CI process as part of PR validation. Linting warning outputs from the command should be included in the PR description for review. 

### Set configuration in AWS SAM template

The `cloud-formation.yaml` AWS SAM template file needs to be updated with the correct parameters for your project. You can use references to outputs from the database infrastructure resources, which should be defined in a separate stack. 

### Testing

Run `make test` to run tests for the Migration Lambda. 

### Apply Migrations
Configure your deployment pipeline to run the following commands:
```bash
# Download atlas binary to be packaged into the Lambda Layer
./scripts/download_atlas.sh 'atlas_layer/bin/'
# Deploy the SAM template
sam deploy --template-file cloud-formation.yaml
```

If using AWS with the provided Lambda-backed custom resource, migrations will automatically be applied when the SAM template is deployed. The Lambda logs will contain details of the outcome.

## Notes
* Any other services or application code that needs to reference the DB schema (e.g. SQLAlchemy models) should be included within this same project, so that they are kept in sync and deployed together.
* The mechanism for applying migrations (Lambda-backed custom resource) can be changed to suit your project needs, while retaining the commands used for local development and in CI.

