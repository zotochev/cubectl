import unittest
from pprint import pprint
from time import sleep

from src.configurator import Configurator
from src.executor import Executor

from src.utils import read_yaml


class TestConfiguratorBasic(unittest.TestCase):
    asset_dir = 'assets/utils_tests/configurator/'
    register_location = (
        asset_dir + '/temp/test_cubectl_configurator.yaml'
    )
    status_file_location = (
            asset_dir + '/temp/enegan_status_file.yaml'
    )
    config_file_location = asset_dir + 'config.yaml'
    report_file_location = asset_dir + 'temp/'

    config = read_yaml(config_file_location)

    init_file_location = asset_dir + 'init.yaml'
    c: Configurator = Configurator(config=config)
    e: Executor = None

    def setUp(self) -> None:
        self.c.init(self.init_file_location, reinit=True)
        self.c.start(app_name='enegan', services=tuple())
        self.e = Executor(self.status_file_location)
        sleep(1)
        print()

    def tearDown(self) -> None:
        self.c.stop(app_name='enegan', services=tuple())

    def test_one(self):
        self.e._update_processes()
        one = self.c.status(app_name=None, report_location=self.report_file_location)
        self.e._update_processes()
        two = self.c.status(app_name=None, report_location=self.report_file_location)
        print(one)
        print('***')
        print(two)
        # self.c.stop(app_name='enegan', services=tuple())
        # self.e.process()
