import unittest
from pprint import pprint

from src.utils.common import read_yaml
from src.utils.nginx_configuration_related import check_service_names_for_duplicates
from src.utils.nginx_configuration_related import get_next_port
from src.utils.nginx_configuration_related import get_all_allocated_ports_by_app


class TestUtilsNginxOne(unittest.TestCase):
    def test_check_service_names_for_duplicates_0(self):
        ports_allocated_by_app = {
            'enegan': {'service_0': 9308, 'service_1': 9309},
            'not_enegan': {'service_2': 9304, 'service_3': 9305}
        }
        _ = check_service_names_for_duplicates(ports_allocated_by_app)

    def test_check_service_names_for_duplicates_1(self):
        ports_allocated_by_app = {
            'enegan': {'service_0': 9308, 'service_1': 9309},
            'not_enegan': {'service_0': 9304, 'service_3': 9305}
        }
        try:
            _ = check_service_names_for_duplicates(ports_allocated_by_app)
        except Exception:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_check_service_names_for_duplicates_2(self):
        ports_allocated_by_app = {
            'enegan': {'service_0': 9308, 'service_1': 9309},
        }
        _ = check_service_names_for_duplicates(ports_allocated_by_app)

    def test_check_service_names_for_duplicates_3(self):
        ports_allocated_by_app = {
            'enegan': {'service_0': 9308},
        }
        _ = check_service_names_for_duplicates(ports_allocated_by_app)

    def test_check_service_names_for_duplicates_4(self):
        ports_allocated_by_app = {
            'enegan': {},
        }
        _ = check_service_names_for_duplicates(ports_allocated_by_app)

    def test_check_service_names_for_duplicates_5(self):
        ports_allocated_by_app = {
        }
        _ = check_service_names_for_duplicates(ports_allocated_by_app)


class TestUtilsNginxGetNextPort(unittest.TestCase):
    def test_get_next_port(self):
        _ = get_next_port()
