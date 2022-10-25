import unittest
from pprint import pprint

from src.utils.common import read_yaml
from src.utils.common import resolve_path


class TestUtilsCommonOne(unittest.TestCase):
    files_assets = {
        'config': ''
    }

    def test_read_yaml(self):
        a = resolve_path('', '')
        print(a)
