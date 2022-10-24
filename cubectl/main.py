from time import sleep
import dotenv
from pathlib import Path
from typing import Optional

import yaml

from . import register_location
from src.utils import resolve_path, read_yaml
from src.initialization_functions import register_application
from src.initialization_functions import create_status_object

from src.models import InitFileModel


def init(init_file: str):
    """
    Registers application in cubectl_application_register.yaml
    Creates status file out of init_file.

    """
    init_config: InitFileModel = read_yaml(
        init_file, validation_model=InitFileModel
    )
    root_dir = init_config.root_dir if init_config.root_dir else Path(init_file).parent
    init_config.root_dir = root_dir
    status_file = resolve_path(
        root_dir=root_dir, file_path=init_config.status_file
    )

    register_application(init_config=init_config.dict())
    status_object = create_status_object(
        init_config=init_config.dict(),
    )

    with open(status_file, 'w') as f:
        yaml.dump(status_object.dict(), f)


def status():
    """
    Shows running applications. If there are more than one.
    /tmp/cubectl_applications.yaml
    """


def main():
    """
    name: Optional[str]
    command: str
    environment: dict[str, str] = dict()  # list of env variables
    env_files: list[str] = list()         # list of env files
    dotenv: bool = True                   # if true (default true) tries to load .env file near command file
    service: bool = True                  # if true (default false) assigns port and nginx config
    """

    init_config_ok = {
        'name': 'test_process',
        # 'command': 'python cubectl/tests/example_services/example_service_0.py',

        'executor': 'python',
        'file': 'cubectl/tests/example_services/example_service_0.py',
        'arguments': {'--name': 'new_name'},
        'dotenv': True,
        'environment': {'TWO': 'TWO2'},
        'env_files': ['cubectl/tests/example_services/environments/local.env']
    }

    # pr = ServiceProcess(init_config=init_config_ok)
    # pr.start()
    # sleep(5)
    # pr.stop()


if __name__ == '__main__':
    main()
