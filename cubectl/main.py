import os

import click
from pathlib import Path
import dotenv

from src.configurator import Configurator, ConfiguratorException
from src.executor import Executor, ExecutorException

from src import config, register_location
from src.utils import (
    resolve_path,
    get_status_file,
    create_nginx_config,
    get_all_allocated_ports_by_app,
    read_yaml,
    check_service_names_for_duplicates,
    check_if_launched_as_root,
    format_report
)


configurator = Configurator(config)
dotenv.load_dotenv()


@click.group()
def cli():
    """
    Script to control processes

    Commands:
        init:
        start:
        stop:
        watch:
        setup-nginx:
    """


@cli.command('init')
@click.argument('init_file')
def init(init_file: str):
    """
    Registers application in cubectl_application_register.yaml
    Creates status file out of init_file.

    This command does not start services. To start service use 'start' command.

    Arguments:
        init_file:  init file path
    """

    init_file = resolve_path(
        root_dir=Path.cwd(), file_path=init_file, return_dir=False
    )
    try:
        configurator.init(init_file=init_file, reinit=True)
    except ConfiguratorException as ce:
        print(f"Initialization failed: {ce}")


@cli.command('start')
@click.argument('app_name', default='all')
@click.argument('services', nargs=-1)
def start(app_name: str, services: tuple):
    """
    Arguments:
        app_name: [Optional] Application name
        services: tuple of services names from init_file
    """

    try:
        configurator.start(app_name=app_name, services=services)
    except ConfiguratorException as ce:
        print(f"Failed to start {app_name}: {ce}")


@cli.command('stop')
@click.argument('app_name', default='all')
@click.argument('services', nargs=-1)
def stop(app_name: str, services: tuple):
    """
    Arguments:
        app_name: [Optional] Application name
        services: tuple of services names from init_file
    """

    try:
        configurator.stop(app_name=app_name, services=services)
    except ConfiguratorException as ce:
        print(f"Failed to stop {app_name}: {ce}")


@cli.command('restart')
@click.argument('app_name', default='all')
@click.argument('services', nargs=-1)
def restart(app_name: str, services: tuple):
    """
    Arguments:
        app_name: [Optional] Application name
        services: tuple of services names from init_file
    """

    try:
        configurator.restart(app_name=app_name, services=services)
    except ConfiguratorException as ce:
        print(f"Failed to restart {app_name}: {ce}")


@cli.command('status')
@click.argument('app_name', default=None)
def status(app_name: str):
    """
    Arguments:
        app_name: [Optional] Application name
    """

    try:
        report = configurator.status(app_name=app_name, report_location=config['report_location'])
        print(format_report(report))
    except ConfiguratorException as ce:
        print(f"Failed to get status for {app_name}: {ce}")


@cli.command('watch')
@click.argument('app_name', default='default')
def watch(app_name):
    """
    Starts monitoring for initializated services

    Arguments:
        app_name:
    """

    status_file = None

    try:
        status_file = get_status_file(
            app_name=app_name, register_location=register_location
        )
    except Exception as e:
        print(f'Failed to retrieve status file for {app_name}. Error: {e}')

    try:
        e = Executor(status_file)
        e.process()
    except ExecutorException as ee:
        print(f'Failed to start {app_name}. Error: {ee}')


@cli.command('setup-nginx')
@click.option('--apply', default=False, is_flag=True)
@click.argument('app_name', default='default')
def setup_nginx(app_name, apply):
    """
    Create nginx config file for services from init file.

    Arguments:
        app_name:
        apply:
    """

    if apply and not check_if_launched_as_root():
        raise Exception('cubectl: setup-nginx: to apply run as the root user.')

    status_file = get_status_file(
        app_name=app_name, register_location=register_location
    )
    status = read_yaml(status_file)
    services = [
        x for x in status.get('services', [])
        if x['init_config']['service']
    ]

    if not services:
        raise Exception('cubectl: no services found in status file.')

    register = read_yaml(register_location)
    ports_by_app = get_all_allocated_ports_by_app(register)
    check_service_names_for_duplicates(ports_by_app)

    ports_by_service = dict()
    for service_ports in ports_by_app.values():
        for service_name, port in service_ports.items():
            ports_by_service[port] = ports_by_service.get(port, [])
            ports_by_service[port].append(service_name)

    nginx_config = create_nginx_config(ports_by_service)

    nginx_config_file = f'cubectl_{app_name}'
    if check_if_launched_as_root():
        nginx_config_file = '/etc/nginx/sites-available/' + nginx_config_file

    with Path(nginx_config_file).open('w') as f:
        print('writing to ', nginx_config_file)
        f.write(nginx_config)

    if apply:
        os.symlink(
            nginx_config_file,
            nginx_config_file.replace('sites-available', 'sites-enabled')
        )


if __name__ == '__main__':
    cli()
