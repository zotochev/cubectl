from pathlib import Path
from cubectl.src.utils import read_yaml
from logging import getLogger


log = getLogger(__file__)

try:
    script_root = Path(__file__).parent.parent
    config = read_yaml(Path(script_root, 'config.yaml'))
except FileNotFoundError:
    # tests
    config = read_yaml('assets/utils_tests/config.yaml')

try:
    temp_dir = Path(config['temp_dir']).resolve()
    log.debug(f'cubectl: src: __init__: temp_dir: {temp_dir}')
    if not temp_dir.is_dir():
        temp_dir.mkdir(parents=True, exist_ok=True)
    config['temp_dir'] = temp_dir
except Exception as e:
    log.critical(f'cubectl: src: __init__: temp_dir={config.get("temp_dir")} '
                 f'from config not accessible. error: {e}'
                 )

register_location = str(Path(config['temp_dir'],
                             'cubectl_application_register.yaml'
                             )
                        )
app_register = str(Path(config['temp_dir'],
                        'cubectl_application_register.yaml'
                        )
                   )
# register_location = config['applications_register']
# default_status_files_dir = config['default_status_files_dir']
