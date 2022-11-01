import os

import click
from pathlib import Path
import dotenv
import logging

from cubectl.src.configurator import Configurator, ConfiguratorException
from cubectl.src.executor import Executor, ExecutorException

from cubectl.src import config, register_location
from cubectl.src.utils import (
    resolve_path,
    get_status_file,
    create_nginx_config,
    get_all_allocated_ports_by_app,
    read_yaml,
    check_service_names_for_duplicates,
    check_if_launched_as_root,
    format_report,
    TelegramMessanger,
    send_message_to_subscribers,
    get_app_name_and_register,
)


configurator = Configurator(config)
# dotenv.load_dotenv(dotenv_path=Path(Path(__file__).parent, '.env'))
# dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)


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
        root_dir=None, file_path=init_file, return_dir=False
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
    app_name_resolved, _ = get_app_name_and_register(
        app_name=app_name,
        register_location=register_location,
        get_default_if_not_found=True,
    )

    if app_name not in ('all', None, 'default', app_name_resolved):
        services = [*services, app_name]
        app_name = app_name_resolved

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

    app_name_resolved, _ = get_app_name_and_register(
        app_name=app_name,
        register_location=register_location,
        get_default_if_not_found=True,
    )
    if app_name not in ('all', None, 'default', app_name_resolved):
        services = [*services, app_name]
        app_name = app_name_resolved

    try:
        log.debug(f'cubectl: main: stopping services: {services}; In app: {app_name}')
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

    app_name_resolved, _ = get_app_name_and_register(
        app_name=app_name,
        register_location=register_location,
        get_default_if_not_found=True,
    )
    if app_name not in ('all', None, 'default', app_name_resolved):
        services = [*services, app_name]
        app_name = app_name_resolved

    try:
        configurator.restart(app_name=app_name, services=services)
    except ConfiguratorException as ce:
        print(f"Failed to restart {app_name}: {ce}")


@cli.command('status')
@click.argument('app_name', default='default')
def status(app_name: str):
    """
    Arguments:
        app_name: [Optional] Application name
    """
    app_name, _ = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )

    try:
        log.debug(f'cubectl: status: getting status for app_name: {app_name}')
        report = configurator.status(app_name=app_name, report_location=config['report_location'])
        print(format_report(report=report, app_name=app_name))
    except ConfiguratorException as ce:
        print(f"Failed to get status for {app_name}: {ce}")


@cli.command('watch')
@click.argument('app_name', default='default')
@click.option('--check', '-c', default=1, help='Period of checking processes status')
def watch(app_name, check):
    """
    Starts monitoring for initializated services

    Arguments:
        app_name:
    """
    app_name, _ = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )

    status_file = None
    telegram_token = os.getenv('CUBECTL_TELEGRAM_TOKEN')
    telegram_subscribers = os.getenv('CUBECTL_TELEGRAM_CHAT_IDS')

    m = None
    if telegram_token:
        m = TelegramMessanger(token=telegram_token)
        m.add_subscribers(ids=telegram_subscribers)

    try:
        status_file = get_status_file(
            app_name=app_name, register_location=register_location
        )
    except Exception as e:
        print(f'Failed to retrieve status file for {app_name}. Error: {e}')

    try:
        log.debug(f'cubectl: main: creating Executor for app: {app_name}, with arguments: {status_file=}; {app_name=}')
        e = Executor(status_file=status_file, meta_info={'app': app_name})
        e.add_messanger(m)
        e.process(cycle_period=check)
    except ExecutorException as ee:
        print(f'Failed to start {app_name}. Error: {ee}')


@cli.command('setup-nginx')
@click.option('--apply', default=False, is_flag=True)
@click.option('--file', default=False, is_flag=True)
@click.argument('app_name', default='default')
def setup_nginx(app_name, apply, file):
    """
    Create nginx config file for services from init file.

    Arguments:
        app_name:
        apply:
        file:
    """
    app_name, _ = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )

    # if apply and not check_if_launched_as_root():
    if apply:
        # raise Exception('cubectl: setup-nginx: to apply run as the root user.')
        raise Exception('cubectl: setup-nginx: apply option not implemented.')

    status_file = get_status_file(
        app_name=app_name, register_location=register_location
    )
    status_dict = read_yaml(status_file)
    services = [
        x for x in status_dict.get('services', [])
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

    if file:
        with Path(nginx_config_file).open('w') as f:
            print('writing to ', nginx_config_file)
            f.write(nginx_config)
    else:
        print(nginx_config)

    # if apply:
    #     os.symlink(
    #         nginx_config_file,
    #         nginx_config_file.replace('sites-available', 'sites-enabled')
    #     )


@cli.command('get-apps')
def get_apps():
    """
    Returns list of applications registered in register.
    """

    log.debug(f'cubectl: main: getting app list from {register_location}')

    app_name, register = get_app_name_and_register(
        app_name=None, register_location=register_location
    )
    apps = [f'* {x["app_name"]}' for x in register]
    if apps:
        print("Registered applications:")
        print(*apps, sep='\n')
    else:
        print('Applications not found.')


@cli.command('get-init-file-example')
def get_init_file_example():
    log.debug(f'cubectl: main: getting init file example.')
    example_file = Path(Path(__file__).parent, 'init-file-example.yaml')
    if example_file.is_file():
        print(example_file.read_text())
    log.warning(f'cubectl: main: no init example found in {example_file}.')


@cli.command('message')
@click.argument('text', default='default')
def message(text):
    telegram_token = os.environ['CUBECTL_TELEGRAM_TOKEN']
    telegram_subscribers = os.environ['CUBECTL_TELEGRAM_CHAT_IDS'].split(',')

    send_message_to_subscribers(
        message=text,
        telegram_chat_ids=telegram_subscribers,
        telegram_token=telegram_token,
    )


if __name__ == '__main__':
    cli()
