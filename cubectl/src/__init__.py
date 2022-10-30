from pathlib import Path
from cubectl.src.utils import read_yaml


try:
    script_root = Path(__file__).parent.parent
    config = read_yaml(Path(script_root, 'config.yaml'))
except FileNotFoundError:
    # tests
    config = read_yaml('assets/utils_tests/config.yaml')

register_location = config['applications_register']
default_status_files_dir = config['default_status_files_dir']
