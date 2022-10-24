import yaml
from pathlib import Path


def get_status_file(app_name, register_location):
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
    return status_file
