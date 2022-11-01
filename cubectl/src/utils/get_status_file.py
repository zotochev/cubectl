import yaml
from pathlib import Path
import logging


log = logging.getLogger(__file__)


def get_status_file(app_name, register_location) -> str:
    app_name, register = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )
    status_file = None

    for app in register:
        if app['app_name'] == app_name:
            status_file = app['status_file']

    if not Path(status_file).is_file():
        log.warning(
            f'cubectl: get_status_file: status_file "{status_file}" '
            f'does not exist.'
        )

    return status_file


AppName = str
RegisterLocation = str


def get_app_name_and_register(
        app_name,
        register_location,
        get_default_if_not_found=True
) -> (AppName, RegisterLocation):
    try:
        with Path(register_location).open() as f:
            register: dict = yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError:
        raise FileNotFoundError(
            f'cubectl: get_status_file: register not found: {register_location}'
        )

    if not register:
        raise ModuleNotFoundError(
            'cubectl: no applications registered (register is empty)'
        )

    registered_apps = [x['app_name'] for x in register]

    if app_name in (None, 'default', 'all'):
        app_name = register[0]['app_name']

    if app_name not in registered_apps:
        if get_default_if_not_found:
            log.warning(
                f'cubectl: application {app_name} not found in register. Assigning app name: {register[0]["app_name"]}'
            )
            return register[0]['app_name'], register
        raise ModuleNotFoundError(
            f'cubectl: application {app_name} not found in register. '
            f'Try to call cubectl_init before().'
        )
    else:
        return app_name, register
