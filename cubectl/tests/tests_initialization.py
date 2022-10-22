import unittest
from pprint import pprint

from cubectl.src.models import ProcessState
from cubectl.src.models import ProcessStatus
from cubectl.src.configurator.configurator import Configurator
from cubectl.src.initialization_functions.application_registration import register_application


class TestInitializationBasic(unittest.TestCase):
    register_location = (
        '/home/mikhail/PycharmProjects/cubectl/cubectl/'
        'tests/assets/temp/cubectl_applications_register.yaml'
    )
    app_name = 'new_init_app'
    init_file_location = '/tmp/init.yaml'

    def test_one(self):
        register_application(
            app_name=self.app_name,
            init_file_path=self.init_file_location,
            register_path=self.register_location
        )
