import unittest
from pprint import pprint
from time import sleep
from pathlib import Path

from src.configurator import Configurator
from src.executor import Executor

from src.utils import read_yaml


class TestConfiguratorBasic(unittest.TestCase):
    asset_dir = str(Path('assets/utils_tests/configurator/').resolve(strict=True))
    register_location = (
        asset_dir + '/temp/cubectl_application_register.yaml'
    )
    status_file_location = (
            asset_dir + '/temp/enegan/status.yaml'
    )
    config_file_location = asset_dir + '/config.yaml'
    report_file_location = asset_dir + '/temp/enegan'

    config = read_yaml(config_file_location)

    init_file_location = asset_dir + '/init.yaml'
    c: Configurator = Configurator(config=config, app_register=register_location)
    e: Executor = None

    def setUp(self) -> None:
        self.c.init(self.init_file_location, reinit=True)
        self.c.start(app_name='enegan', services=tuple())
        self.e = Executor(self.status_file_location)
        sleep(1)
        print()

    def tearDown(self) -> None:
        self.c.stop(app_name='enegan', services=tuple())
        self.e._stop_all_processes()

    def test_one(self):
        status_object = read_yaml(self.status_file_location)

        self.e._update_processes(status_object=status_object)

        one = self.c.status(app_name='enegan')

        status_object = read_yaml(self.status_file_location)
        self.e._update_processes(status_object=status_object)

        two = self.c.status(app_name='enegan')
        sleep(2)
        print(one)
        print('***')
        print(two)
