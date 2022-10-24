import yaml
from pathlib import Path
import logging

# from cubectl import register_location
from src.utils import resolve_path, read_yaml
from src.initialization_functions import register_application
from src.initialization_functions import create_status_object

from src.models import InitFileModel, ProcessState


log = logging.getLogger(__file__)


class Configurator:
    """
    Inits status file.
    Opens status file and sets it in requested state.
    """

    def __init__(self, config: dict = None):
        if not config:
            config = dict()
        self._config = config
        self._app_register = config.get('applications_register', '/tmp/cubectl_application_register.yaml')

    def _get_app_register(self, app_name: str) -> dict:
        register = Path(self._app_register).resolve()
        if not register.is_file():
            raise Exception('cubectl: No register found.')
        with register.open() as f:
            register_dict: dict = yaml.load(f, Loader=yaml.FullLoader)
            if not register_dict:
                raise Exception('cubectl: Register is empty.')

        try:
            return register_dict[app_name]
        except Exception:
            return list(register_dict.values())[0]

    def _get_status(self, app_name: str):
        register = self._get_app_register(app_name=app_name)
        status_file = Path(register['status_file'])

        with status_file.open() as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def init(self, init_file: str, reinit: bool = False):
        """
        todo:
            * create status file out of init file
        """

        init_config: InitFileModel = read_yaml(
            init_file, validation_model=InitFileModel
        )
        root_dir = init_config.root_dir if init_config.root_dir else Path(init_file).parent
        init_config.root_dir = str(root_dir)

        status_file = Path(
            init_config.status_file_dir,
            f'{init_config.installation_name}_status_file.yaml'
        )

        register_application(
            init_config=init_config.dict(),
            status_file=str(status_file),
            register_path=self._app_register,
        )
        status_object = create_status_object(
            init_config=init_config.dict(),
        )

        status_file = Path(status_file)
        if status_file.is_dir():
            status_file = Path(status_file, '')

        if Path(status_file).is_file() and not reinit:
            return

        with open(status_file, 'w') as f:
            yaml.dump(status_object.dict(), f)

    def _change_process_state(self, app_name: str, services: tuple, state: ProcessState):
        """
        1. status file does not have service set up in init
        2. status file has service set up in init
        3. status of service does not conflict with command
        4. status of service conflicts with command

        alg:
            * check are there any applications
                if len(applications) == 0 raise No applications found
            * check if app_name == any of application names
                * False - chose first app (app_name = applications[0]) and add app_name to services
                * True - choose app_name application
            * open status file for app_name
            * change it to started
            * save new status file
        """

        register = self._get_app_register(app_name=app_name)
        status_file = Path(
            register['status_file']
        )
        status = self._get_status(app_name=app_name)

        processes_names = [x['init_config']['name'] for x in status['services']]
        services_to_start = [x for x in services if x in processes_names]
        not_existing = [x for x in services if x not in processes_names]
        if not_existing:
            log.warning(
                f'cubectl: configurator: processes not found: {not_existing}'
            )

        if app_name.lower() == 'all' or not services:
            services_to_start = processes_names
        elif app_name in processes_names:
            services_to_start.append(app_name)

        for process in status['services']:
            if process['init_config']['name'] in services_to_start:
                process['system_data']['state'] = state.value

        with status_file.open('w') as new_status_file:
            yaml.dump(status, new_status_file)
        pass

    def start(self, app_name: str, services: tuple):
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.started
        )

    def stop(self, app_name: str, services: tuple):
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.stopped
        )
