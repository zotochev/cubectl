import yaml
from pathlib import Path
import logging


log = logging.getLogger(__file__)


def get_status_file(app_name, register_location) -> str:
    # try:
    #     with Path(register_location).open() as f:
    #         register: dict = yaml.load(f, Loader=yaml.Loader)
    # except FileNotFoundError:
    #     raise FileNotFoundError(
    #         f'cubectl: get_status_file: register not found: {register_location}'
    #     )
    #
    # if not register:
    #     raise ModuleNotFoundError(
    #         'cubectl: no applications registered (register is empty)'
    #     )
    #
    # if app_name in (None, 'default'):
    #     log.warning(
    #         'cubectl: get_status_file: app_name choosed automatically '
    #         'from not ordered type dict.'
    #     )
    #     app_name = list(register.keys())[0]
    #
    # try:
    #     if app_name not in register:
    #         raise ModuleNotFoundError(
    #             f'cubectl: application {app_name} not found in register. '
    #             f'Try to call cubectl_init before().'
    #         )
    #     else:
    #         status_file = register[app_name]['status_file']
    # except KeyError as e:
    #     raise TypeError(
    #         f'cubectl: get_status_file: invalid register format: {register}.\n'
    #         f'key error: "{e}" for app "{app_name}".'
    #     )
    app_name, register = get_app_name_and_register(
        app_name=app_name, register_location=register_location
    )
    status_file = register[app_name]['status_file']

    if not Path(status_file).is_file():
        log.warning(
            f'cubectl: get_status_file: status_file "{status_file}" '
            f'does not exist.'
        )

    return status_file


def get_app_name_and_register(app_name, register_location) -> (str, str):
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

    if app_name in (None, 'default'):
        log.warning(
            'cubectl: get_status_file: app_name choosed automatically '
            'from not ordered type dict.'
        )
        app_name = list(register.keys())[0]

    if app_name not in register:
        raise ModuleNotFoundError(
            f'cubectl: application {app_name} not found in register. '
            f'Try to call cubectl_init before().'
        )
    else:
        return app_name, register
