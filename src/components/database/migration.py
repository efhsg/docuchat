from alembic.config import Config as AlembicConfig
from alembic import command

from config import Config
from components.database.mysql_connector import MySQLConnector
from components.logger.logger import Logger


class Migration:
    logger = Logger.get_logger()

    def __init__(self, config=None, connection=None):
        self.config = config or Config()
        self.connection = connection or MySQLConnector().get_connection()

    def get_current_migration_version(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1"
                )
                result = cursor.fetchone()
                if result:
                    return result["version_num"]
                else:
                    return None
        except Exception as e:
            self.logger.error(f"Unable to fetch current migration version: {e}")
            return None

    def has_latest_migration_run(self):
        current_version = self.get_current_migration_version()
        return current_version == self.config.latest_migration_version

    def check_and_apply_migrations(self):
        alembic_cfg = AlembicConfig(
            self.config.project_root / "src/alembic/alembic.ini"
        )

        if not self.has_latest_migration_run():
            self.logger.info("Data model not up to date. Applying database migrations.")
            try:
                command.upgrade(alembic_cfg, "head")
                self.logger.info("Database migrations applied successfully!")
            except Exception as e:
                self.logger.error(
                    f"Failed to automatically apply migrations. Please review manually. Error: {e}"
                )
                raise
