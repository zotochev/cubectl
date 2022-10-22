import yaml
from pathlib import Path


def register_application(
        app_name: str,
        init_file_path: str,
        register_path: str = '/tmp/cubectl_applications_register.yaml'
):
    register_path = Path(register_path)

    if register_path.is_file():
        with register_path.open() as f:
            register = yaml.load(f, Loader=yaml.FullLoader)
    else:
        register = dict()

    register[app_name] = {
        ''
    }

