from pathlib import Path
from src.utils import read_yaml


try:
    config = read_yaml('config.yaml')
except FileNotFoundError:
    # tests
    config = read_yaml('assets/utils_tests/config.yaml')

register_location = config['applications_register']
default_status_files_dir = config['default_status_files_dir']
