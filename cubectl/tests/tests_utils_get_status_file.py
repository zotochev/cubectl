import unittest
from pprint import pprint

from src.utils.common import read_yaml
from src.utils.get_status_file import get_status_file


class TestUtilsGetStatusFile(unittest.TestCase):
    register_location_ok = (
        'assets/utils_tests/test_cubectl_applications_register.yaml'
    )
    register_location_ng = (
        'assets/utils_tests/test_cubectl_applications_register_ng.yaml'
    )
    register_location_empty = (
        'assets/utils_tests/test_cubectl_applications_register_empty.yaml'
    )
    init_file_location = 'assets/utils_tests/init.yaml'
    status_file_location = 'assets/utils_tests/status_file.yaml'
    init_config = read_yaml(init_file_location)

    register_ok = read_yaml(register_location_ok)
    register_empty = read_yaml(register_location_empty)
    register_ng = read_yaml(register_location_ng)

    def test_get_status_file(self):
        _ = get_status_file(app_name=None, register_location=self.register_location_ok)

    def test_get_status_file_with_app_name(self):
        _ = get_status_file(app_name='enegan', register_location=self.register_location_ok)

    def test_get_status_file_not_exists_app(self):
        try:
            _ = get_status_file(app_name='sadsa', register_location=self.register_location_ok)
        except ModuleNotFoundError as e:
            pass

    def test_get_register_not_exists_app(self):
        try:
            _ = get_status_file(app_name=None, register_location='dsadssad')
        except FileNotFoundError as e:
            pass

    def test_get_register_empty(self):
        try:
            _ = get_status_file(app_name=None, register_location=self.register_location_empty)
        except ModuleNotFoundError as e:
            pass

    def test_get_register_empty_app_name(self):
        try:
            _ = get_status_file(app_name='sdas', register_location=self.register_location_empty)
        except ModuleNotFoundError as e:
            pass

    def test_get_register_ng(self):
        try:
            a = get_status_file(app_name=None, register_location=self.register_location_ng)
        except (ModuleNotFoundError, TypeError, KeyError):
            return
        self.assertTrue(False)
