import logging
import re
import subprocess

from sqlalchemy import text

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

logger = logging.getLogger(__name__)


# Define ANSI escape codes for text colors
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
RESET = "\033[0m"


def colorise_sql(content):
    # Define keywords to search for
    REMOVE_ACTIONS = ["DROP", "ALTER"]
    MODIFY_ACTIONS = ["UPDATE"]
    CREATE_ACTIONS = ["CREATE", "INSERT"]

    # Regular expression patterns to match each keyword
    remove_pattern = re.compile("|".join(REMOVE_ACTIONS), re.IGNORECASE)
    modify_pattern = re.compile("|".join(MODIFY_ACTIONS), re.IGNORECASE)
    create_pattern = re.compile("|".join(CREATE_ACTIONS), re.IGNORECASE)

    # Loop through each line of the SQL output and colorize according to the action
    output_lines = []
    for line in content.split("\n"):
        if remove_pattern.search(line):
            line = RED + line + RESET
        elif modify_pattern.search(line):
            line = BLUE + line + RESET
        elif create_pattern.search(line):
            line = GREEN + line + RESET
        output_lines.append(line)

    return "\n".join(output_lines)


def colorise_check(content):
    # Regular expression patterns to match each keyword
    error_pattern = re.compile("ERROR")
    info_pattern = re.compile("INFO")

    # Loop through each line of the check output and colorize according to the log type
    output_lines = []
    for line in content.split("\n"):
        if error_pattern.search(line):
            line = RED + line + RESET
        elif info_pattern.search(line):
            line = GREEN + line + RESET
        output_lines.append(line)

    return "\n".join(output_lines)


# returns true if the user wants to skip the migrations
def verify_sql(alembic_config, current_rev) -> bool:
    # Create an Alembic script directory object
    script_directory = ScriptDirectory.from_config(Config("alembic.ini"))
    revisions = [
        rev.revision for rev in script_directory.walk_revisions("base", "heads")
    ]

    # Set the target revision and source revision
    target_revision = next(iter(revisions), None)
    source_revision = current_rev

    if target_revision != source_revision:
        if source_revision is not None:
            console_command = [
                "alembic",
                "upgrade",
                f"{source_revision}:{target_revision}",
                "--sql",
            ]
        else:
            console_command = ["alembic", "upgrade", "head", "--sql"]
        try:
            result = subprocess.run(
                console_command, capture_output=True, text=True, check=True
            )
            logger.info(colorise_sql(result.stdout))
        except subprocess.CalledProcessError as e:
            logger.error(
                "Command '%s' returned non-zero exit status %d. Output: %s",
                e.cmd,
                e.returncode,
                e.stderr,
            )
            raise e

        # Ask the user to approve the migration
        response = input("Do you want to apply these migrations? [y/N] ")

        if response.lower() in ["y", "ye", "yes"]:
            # Upgrade the database to the latest revision
            command.upgrade(alembic_config, "head")
            return False
        else:
            # NB: we've decided that the server should continue to run even if you choose to skip the migrations
            logger.info(
                "Skipping schema migrations, your models and database will now be out of sync"
            )
            return True


def perform_schema_migrations(config, session):
    # Create an Alembic configuration object
    alembic_config = Config("alembic.ini")
    # Overwrite sqlalchemy.url with our connection_string
    alembic_config.set_main_option("sqlalchemy.url", config["connection_string"])

    # prompt for migration
    # this will deliberately fail on cloud environments (no std in to read from)
    # locally, the user can control this
    logger.info(
        "Detected local or cloud environment, prompting for schema migrations if required"
    )

    try:
        result = session.execute(text("SELECT version_num FROM alembic_version"))
        current_rev = result.scalar()
        session.close()
    except Exception as e:
        session.close()
        raise e

    # let the user check to see if they want to apply new changes
    skipped = verify_sql(alembic_config, current_rev)
    if skipped:
        return

    # check for differences between schemas
    console_command = ["alembic", "check"]
    result = subprocess.run(console_command, capture_output=True, text=True)

    if result.returncode == 0:
        # DB schema already in sync with models
        logger.info(colorise_check(result.stdout))
    else:
        # New migration needed to sync DB schema with models
        logger.info(colorise_check(result.stderr))

        # Ask the user to approve the migration
        migration_name = input(
            "If you're ready to create a new migration, please provide a descriptive name?\nOtherwise, please continue making models changes and create migration when you're done.\nThe less migrations the better. \n Name: "
        )
        while migration_name == "":
            migration_name = input("Please select a name that is not blank \n Name: ")

        console_command = [
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            migration_name,
        ]
        result = subprocess.run(console_command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(colorise_sql(result.stdout))
        else:
            logger.info(colorise_check(result.stderr))

        logger.info(
            "Please check the following SQL output is correct before applying this migration. If you want to make any changes to the auto-generated migration hit N, make your changes and then rerun the server."
        )

        # let the user check to see if they want to edit the migration script before apply new changes
        verify_sql(alembic_config, current_rev)
