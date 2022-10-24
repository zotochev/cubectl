import click
import yaml
from pathlib import Path

from src.configurator import Configurator
from src.executor import Executor

from cubectl import config, register_location
from src.utils import resolve_path, get_status_file, create_nginx_config


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
    status_file = get_status_file(
        app_name=app_name, register_location=register_location
    )

    e = Executor(status_file)
    e.process()


@cli.command('setup-nginx')
@click.argument('app_name', default='default')
def setup_nginx(app_name):
    status_file = get_status_file(
        app_name=app_name, register_location=register_location
    )
    services = [
        x for x in status_file.get('services', [])
        if x['init_config']['service']
    ]

    if not services:
        raise Exception('cubectl: no services found in status file.')

    nginx_config = create_nginx_config()


if __name__ == '__main__':
    cli()
