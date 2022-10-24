from time import sleep
import dotenv
from pathlib import Path
from typing import Optional
import click

import yaml

from cubectl import register_location
from src.utils import resolve_path, read_yaml
from src.initialization_functions import register_application
from src.initialization_functions import create_status_object

from src.models import InitFileModel


@click.group()
def cli():
    """
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

    # if command == 'init':
    #     init_file = args
    #
    # if command == 'start':
    #     service_name = args
    #
    # if command == 'start-all':
    #     service_name = args


@cli.command('init')
@click.argument('init_file')
def init(init_file: str):
    """
    Registers application in cubectl_application_register.yaml
    Creates status file out of init_file.

    Arguments:
        init_file:  init file path
    """
    init_file = resolve_path(
        root_dir=Path.cwd(), file_path=init_file, return_dir=False
    )

    init_config: InitFileModel = read_yaml(
        init_file, validation_model=InitFileModel
    )
    root_dir = init_config.root_dir if init_config.root_dir else Path(init_file).parent
    init_config.root_dir = str(root_dir)
    # status_file = resolve_path(
    #     root_dir=root_dir, file_path=init_config.status_file, return_dir=False
    # )
    status_file = Path(
        init_config.status_file_dir,
        f'{init_config.installation_name}_status_file.yaml'
    )

    # register_path = resolve_path(
    #     root_dir=root_dir, file_path='tests/assets/temp/cubectl_applications_register.yaml'
    # )
    register_application(
        init_config=init_config.dict(),
        status_file=str(status_file),
        register_path=register_location,
    )
    status_object = create_status_object(
        init_config=init_config.dict(),
    )

    status_file = Path(status_file)
    if status_file.is_dir():
        status_file = Path(status_file, '')
    with open(status_file, 'w') as f:
        yaml.dump(status_object.dict(), f)


@cli.command('start')
@click.argument('services', nargs=-1)
def status(services: tuple):
    """
    Shows running applications. If there are more than one.
    /tmp/cubectl_applications.yaml
    """
    print(f'hi from start: {services}')


if __name__ == '__main__':
    cli()
