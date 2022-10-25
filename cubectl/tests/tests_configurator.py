import unittest
from pprint import pprint

from src.configurator.configurator import Configurator


class TestConfiguratorBasic(unittest.TestCase):
    def test_one(self):
        c = Configurator()
