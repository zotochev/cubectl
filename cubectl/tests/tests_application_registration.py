import unittest
from pathlib import Path
from pprint import pprint

from src.initialization_functions.application_registration import register_application
from src.initialization_functions.application_registration import init_service_status
from src.initialization_functions.application_registration import create_status_object
from src.utils.common import read_yaml

from src.models import InitProcessConfig


class TestInitializationBasic(unittest.TestCase):
    register_location = (
        'assets/utils_tests/test_cubectl_applications_register.yaml'
    )
    init_file_location = 'assets/utils_tests/init.yaml'
    status_file_location = 'assets/utils_tests/status_file.yaml'
    init_config = read_yaml(init_file_location)

    def test_register_application(self):
        """
        init_config: dict,
        status_file: str,
        register_path: str = '/tmp/cubectl_applications_register.yaml'
        """

        register_application(
            init_config=self.init_config,
            status_file=self.status_file_location,
            register_path=self.register_location,
        )


class TestInitializationCreateStatusObject(unittest.TestCase):
    init_file_location = 'assets/utils_tests/init_create_status.yaml'
    status_file_location = 'assets/utils_tests/status_file.yaml'
    init_config = read_yaml(init_file_location)
    process_config_dict = {
        'name': 'service_0',

        'executor': 'python',
        'file': 'assets/example_services/example_service_0.py',
        'arguments': {'--name': 'name_0'},

        'environment': {
            'FOO': 'BAR',
            'ONE': 'ONE1',
        },
        'env-files': [],
        'dotenv': False,
        'service': True,
        'port': 1234,
    }
    process_config = InitProcessConfig(**process_config_dict)

    def test_init_service_status_one(self):
        _ = init_service_status(
            root_dir='q', process_init_config=self.process_config
        )

    def test_init_service_status_two(self):
        _ = init_service_status(
            root_dir=str(Path.cwd()), process_init_config=self.process_config
        )

    def test_create_status_object_one(self):
        _ = create_status_object(init_config=self.init_config)
