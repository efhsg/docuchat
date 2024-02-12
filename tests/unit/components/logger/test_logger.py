import os
import unittest
from unittest.mock import patch

from components.logger.logger import Logger


class TestLoggerConfig(unittest.TestCase):
    @patch.dict(os.environ, {"RUNNING_IN_DOCKER": "true"})
    def test_get_config_path_docker(self):
        config_path = Logger._get_config_path()
        self.assertTrue(config_path.name.endswith("logging.docker.ini"))

    @patch.dict(os.environ, {"RUNNING_IN_DOCKER": "false"})
    def test_get_config_path_venv(self):
        config_path = Logger._get_config_path()
        self.assertTrue(config_path.name.endswith("logging.venv.ini"))

    # Test edge case: No 'RUNNING_IN_DOCKER' environment variable
    @patch.dict(os.environ, {})
    def test_get_config_path_no_environment_variable(self):
        config_path = Logger._get_config_path()
        self.assertTrue(
            config_path.name.endswith("logging.venv.ini")
        )  # Assumes a default
