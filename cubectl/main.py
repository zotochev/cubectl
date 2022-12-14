import os
import sys
import signal
import time

import click
from pathlib import Path
import logging
from pprint import pprint
import dotenv
import yaml

from cubectl.src.configurator import Configurator, ConfiguratorException
from cubectl.src.executor import Executor, ExecutorException

from cubectl.src import (
    config,
    register_location,
    temp_dir,
    app_register,
)
from cubectl.src.utils import (
    resolve_path,
    get_status_file,
    create_nginx_config,
    get_all_allocated_ports_by_app,
    read_yaml,
    check_service_names_for_duplicates,
    check_if_launched_as_root,
    format_report,
    format_logs_response,
    TelegramMessanger,
    send_message_to_subscribers,
    get_app_name_and_register,
)


configurator = Configurator(config, app_register=register_location)
executor: Executor = None
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)
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
@click.option('--override', default=False, is_flag=True)
def init(init_file: str, override: bool):
    """
    Registers application in cubectl_application_register.yaml
    Creates status file out of init_file.

    This command does not start services. To start service use 'start' command.

    Arguments:
        init_file:  init file path.
        override: flag to override app in register if exists.
    """

    init_file = resolve_path(
        root_dir=None, file_path=init_file, return_dir=False
    )
    try:
        configurator.init(init_file=init_file, reinit=override)
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
        report = configurator.status(
            app_name=app_name,
            # report_location=config['report_location'],
        )
        print(format_report(report=report, app_name=app_name))
    except ConfiguratorException as ce:
        print(f"Failed to get status for {app_name}: {ce}")


@cli.command('logs')
@click.argument('app_name', default='default')
@click.argument('services', nargs=-1)
@click.option('--full', default=False, is_flag=True)
def logs(app_name: str, services: tuple, full: bool):
    """
    Arguments:
        app_name: [Optional] Application name
        services:
        full: if not supplied only new logs will be showed.
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
        log.debug(f'cubectl: logs: getting logs for app_name: {app_name}')
        report = configurator.get_logs(
            app_name=app_name,
            services=services,
            # logs_buffer_dir=config['log_buffer_location'],
            latest=(not full),
        )
        if isinstance(report, dict):
            print(format_logs_response(logs_response=report, app_name=app_name))
        else:
            print(report)
    except ConfiguratorException as ce:
        print(f"Failed to get status for {app_name}: {ce}")


def handler_stop(signum, frame):
    stop_func = stop.callback
    try:
        app_name, register = get_app_name_and_register(
            app_name=None, register_location=register_location
        )
        apps = [x["app_name"] for x in register]
    except FileNotFoundError:
        apps = []

    for app in apps:
        log.info(f'cubectl: main: handling signal: stopping {app}.')
        stop_func(app, tuple())

    if executor is not None:
        executor._stop_all_processes()

    sys.exit(0)


signal.signal(signal.SIGINT, handler_stop)
signal.signal(signal.SIGABRT, handler_stop)
signal.signal(signal.SIGTERM, handler_stop)


@cli.command('watch')
@click.argument('app_name', default='default')
@click.option('--check', '-c', default=1, help='Period of checking processes status')
def watch(app_name, check):
    """
    Starts monitoring for initializated services

    Arguments:
        app_name:
        check: Period of checking processes status.
    """
    app_name, register = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )
    os.environ['CUBECTL_WATCHER_CHECK_PERIOD'] = str(check)

    status_file = None
    telegram_token = os.getenv('CUBECTL_TELEGRAM_TOKEN')
    telegram_subscribers = os.getenv('CUBECTL_TELEGRAM_CHAT_IDS')

    m = None
    if telegram_token:
        m = TelegramMessanger(token=telegram_token)
        m.add_subscribers(ids=telegram_subscribers)
        log.debug(
            'cubectl: main: watch: telegram messanger successfully configured.'
        )
    else:
        log.warning(
            f'cubectl: main: watch: telegram messanger was not '
            f'configured because env variables was not supplied.\n'
            f'CUBECTL_TELEGRAM_TOKEN={telegram_token}; CUBECTL_TELEGRAM_CHAT_IDS={telegram_subscribers}\n'
        )

    try:
        status_file = get_status_file(
            app_name=app_name, register_location=register_location
        )
    except Exception as e:
        log.error(f'Failed to retrieve status file for {app_name}. Error: {e}')

    try:
        app_index = -1
        for i in range(len(register)):
            if register[i]['app_name'] == app_name:
                app_index = i
                register[i]['watcher_pid'] = os.getpid()
                break
        if app_index != -1:
            with Path(register_location).open('w') as f:
                yaml.dump(register, f)
    except Exception as e:
        log.error(f'cubectl: main: watch: updating of register with watcher pid failed: {e}')

    try:
        log.debug(f'cubectl: main: creating Executor for app: {app_name}, with arguments: {status_file=}; {app_name=}')

        global executor

        executor = Executor(status_file=status_file, meta_info={'app': app_name})
        executor.add_messanger(m)
        executor.process(cycle_period=check)
    except ExecutorException as ee:
        log.error(f'Failed to start {app_name}. Error: {ee}')


@cli.command('get-nginx-config')
@click.option('--apply', default=False, is_flag=True)
@click.option('--file', default=False, is_flag=True)
@click.argument('app_name', default='default')
def get_nginx_config(app_name, apply, file):
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
        nginx_apply_instruction = (
            'sudo bash -c "echo \"$(cubectl setup-nginx)\" > /etc/nginx/cubectl.conf"\n'
            'sudo ln -s /etc/nginx/sites-available/cubectl.conf /etc/nginx/sites-enabled/cubectl.conf\n'
        )
        log.warning(f'cubectl: get-nginx-config: --apply option not '
                    f'implemented. You can try to use:\n'
                    f'{nginx_apply_instruction}'
                    )
        file = True

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
            print('Nginx config created: ', nginx_config_file)
            f.write(nginx_config)
    else:
        print(nginx_config)

    # todo uncomment in case implementation of --apply argument
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

    try:
        app_name, register = get_app_name_and_register(
            app_name=None, register_location=register_location
        )
        apps = [f'* {x["app_name"]}' for x in register]
    except FileNotFoundError:
        apps = []

    if apps:
        print("Registered applications:")
        print(*apps, sep='\n')
    else:
        print('Applications not found.')


@cli.command('kill')
@click.argument('app_name')
def kill(app_name: str):
    """
    command to kill app watcher.

    Arguments:
        app_name: [Optional] Application name
    """

    _, register = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )

    try:
        for app in register:
            if app['app_name'] == app_name:
                watcher_pid = int(app['watcher_pid'])
                os.kill(watcher_pid, signal.SIGTERM)
                log.debug(f'cubectl: kill: app_name: {app_name}')
                return

        log.error(f'cubectl: kill: app_name: {app_name} not found.')
    except Exception as e:
        log.error(f'cubectl: kill: app_name: {app_name} failed: {e}.')


@cli.command('get-init-file-example')
def get_init_file_example():
    log.debug(f'cubectl: main: getting init file example.')
    example_file = Path(Path(__file__).parent, 'init-file-example.yaml')
    if example_file.is_file():
        print(example_file.read_text())
    else:
        log.warning(f'cubectl: main: no init example found in {example_file}.')


@cli.command('clean')
@click.argument('app_name')
def clean(app_name: str):
    try:
        _, register = get_app_name_and_register(
            app_name=None, register_location=register_location
        )
    except FileNotFoundError as fnf:
        print(fnf)
        return
    registered_apps = [x['app_name'] for x in register]
    delete_temp_dir = False

    if app_name in ('all', 'full'):
        apps_to_delete = register
        if app_name == 'full':
            delete_temp_dir = True
    else:
        if app_name not in registered_apps:
            log.warning(
                f'cubectl: main: clean: app {app_name}, not found in register.'
            )
            return
        apps_to_delete = [x for x in register if x['app_name'] == app_name]

    for app in apps_to_delete:
        app_dir = app['app_name']
        for _name, _file in app.items():
            if _name != 'app_name':
                Path(_file).unlink(missing_ok=True)
        try:
            Path(temp_dir, app_dir).rmdir()
        except Exception as e:
            log.error(f'cubectl: main: clean: temp dir for app {app_name} '
                      f'was not deleted. error: {e}')

    if delete_temp_dir:
        Path(register_location).unlink(missing_ok=True)
        try:
            Path(temp_dir).rmdir()
        except Exception as e:
            log.error(f'cubectl: main: clean: temp dir for cubectl '
                      f'was not deleted. error: {e}')


@cli.command('message')
@click.argument('text', default='default')
def message(text):
    telegram_token = os.environ['CUBECTL_TELEGRAM_TOKEN']
    telegram_subscribers = os.environ['CUBECTL_TELEGRAM_CHAT_IDS'].split(',')

    if telegram_token and telegram_subscribers:
        send_message_to_subscribers(
            message=text,
            telegram_chat_ids=telegram_subscribers,
            telegram_token=telegram_token,
        )


if __name__ == '__main__':
    print()
    cli()
