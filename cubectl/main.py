import click
import yaml
from pathlib import Path

from src.configurator import Configurator
from src.executor import Executor

from cubectl import config, register_location
from src.utils import resolve_path


configurator = Configurator(config)


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
    configurator.init(init_file=init_file, reinit=True)


@cli.command('start')
@click.argument('app_name', default='all')
@click.argument('services', nargs=-1)
def status(app_name: str, services: tuple):
    configurator.start(app_name=app_name, services=services)


@cli.command('stop')
@click.argument('app_name', default='all')
@click.argument('services', nargs=-1)
def status(app_name: str, services: tuple):
    configurator.stop(app_name=app_name, services=services)


@cli.command('watch')
@click.argument('app_name', default='default')
def watch(app_name):
    with Path(register_location).open() as f:
        register: dict = yaml.load(f, Loader=yaml.Loader)

    if not register:
        raise Exception(
            'cubectl: no applications registered (register is empty)'
        )
    elif app_name == 'default':
        # fixme change register from dict to list
        #   dicts are not ordered and getting first element is impossible

        status_file = list(register.values())[0]['status_file']
    elif app_name not in register:
        raise Exception(
            f'cubectl: application {app_name} not found in register. '
            f'Try to call cubectl init before.'
        )
    else:
        status_file = register[app_name]['status_file']

    e = Executor(status_file)
    e.process()


if __name__ == '__main__':
    cli()
