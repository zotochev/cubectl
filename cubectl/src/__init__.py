from src.utils import read_yaml


config = read_yaml('config.yaml')
register_location = config['applications_register']
default_status_files_dir = config['default_status_files_dir']
