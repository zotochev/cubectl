# from src.utils import read_yaml
# from pathlib import Path
#
#
# try:
#     config = read_yaml('config.yaml')
# except FileNotFoundError:
#     config = read_yaml('../config.yaml')
#
# temp_dir = Path(config.get('temp_dir', '/tmp/cubectl'))
# temp_dir.mkdir(parents=True, exist_ok=True)
#
# register_location = config['applications_register']
# default_status_files_dir = config['default_status_files_dir']

from cubectl.main import cli
