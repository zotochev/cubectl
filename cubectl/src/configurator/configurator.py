import yaml
from pathlib import Path
import logging
from functools import reduce
from time import sleep
import uuid

from cubectl.src.utils import read_yaml
from cubectl.src.initialization_functions import register_application
from cubectl.src.initialization_functions import create_status_object

from cubectl.src.models import InitFileModel, ProcessState, SetupStatus


log = logging.getLogger(__file__)


class ConfiguratorException(Exception):
    pass


class Configurator:
    """
    Inits status file.
    Opens status file and sets it in requested state.
    """

    def __init__(self, config: dict, app_register: str):
        if not config:
            raise ConfiguratorException('please supply valid config file.')

        self._config = config
        self._temp_dir = config['temp_dir']
        # self._app_register = str(Path(self._temp_dir,
        #                               'cubectl_application_register.yaml'
        #                               )
        #                          )
        self._app_register = app_register

    def _assign_ports_to_services(self, status):
        ports_by_app = _get_all_allocated_ports_by_app(app_register=self._app_register)
        allocated_ports = []
        if not ports_by_app:
            pass
        elif len(ports_by_app) == 1:
            if list(ports_by_app.values()):
                allocated_ports = list(ports_by_app.values())[0]
        else:
            allocated_ports = reduce(
                lambda x, y: [*x, *y], list(ports_by_app.values())
            )

        if allocated_ports:
            port = max(allocated_ports)
        else:
            port = self._config.get('init_port_number', 9300)

        for service in status.services:
            # service: InitProcessConfig
            if service.init_config.service:
                service.service_data.port = service.init_config.port
                if service.init_config.port is None:
                    port += 1
                    allocated_ports.append(port)
                    service.service_data.port = port
        return status

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
        # creating app temp directory
        Path(
            self._temp_dir, init_config.installation_name
        ).mkdir(parents=True, exist_ok=True)

        temp_files = register_application(
            init_config=init_config.dict(),
            register_path=self._app_register,
            temp_files_dir=self._temp_dir,
            reinit=reinit,
        )
        status_file = temp_files['status_file']

        status_object = create_status_object(
            init_config=init_config.dict(),
        )
        status_object = self._assign_ports_to_services(status=status_object)

        status_file = Path(status_file)
        if status_file.is_dir():
            status_file = Path(status_file, '')

        if Path(status_file).is_file() and not reinit:
            log.warning('cubectl: main: init: status file was not overriden '
                        'because reinit=False.')
            raise ValueError('Status file already exists.')

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

        register = _get_app_register(app_name=app_name, app_register=self._app_register)
        status_file = Path(
            register['status_file']
        )
        status = _get_status(app_name=app_name, app_register=self._app_register)

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

    def start(self, app_name: str, services: tuple):
        log.debug(f'cubectl: configurator: app: {app_name}; starting: {services}')
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.started
        )

    def stop(self, app_name: str, services: tuple):
        log.debug(f'cubectl: configurator: app: {app_name}; stopping: {services}')
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.stopped
        )

    def restart(self, app_name: str = None, services: tuple = tuple()):
        register = _get_app_register(app_name=app_name, app_register=self._app_register)
        status_file = Path(
            register['status_file']
        )
        status = SetupStatus(
            **_get_status(app_name=app_name, app_register=self._app_register)
        )

        status.jobs = {
            str(uuid.uuid4()): {
                'restart': {'services': services}
            }
        }
        with status_file.open('w') as new_status_file:
            yaml.dump(status.dict(), new_status_file)

    def status(self, app_name: str = None):
        """
        Arguments:
            app_name:

        """

        # getting status file
        register = _get_app_register(app_name=app_name, app_register=self._app_register)
        report_file = register['status_report']
        log.debug(f"cubectl: configurator: creating report: {report_file}")
        status_file = Path(register['status_file'])
        status = SetupStatus(
            **_get_status(app_name=app_name, app_register=self._app_register)
        )
        # getting status file

        status.jobs = {
            str(uuid.uuid4()): {
                'get_report': {'report_file': report_file}
            }
        }

        report_file_path = Path(report_file)
        report_file_path.touch()

        log.debug(f"cubectl: configurator: updating status file: {status_file}")
        with status_file.open('w') as new_status_file:
            yaml.dump(status.dict(), new_status_file)

        init_time_changed = report_file_path.stat().st_mtime
        report = None

        for _ in range(self._config.get('report_number_of_cycles', 5)):
            sleep(self._config.get('report_retry_wait_time', 1))
            last_time_changed = report_file_path.stat().st_mtime
            if init_time_changed < last_time_changed:
                return read_yaml(report_file)
        return report

    def get_logs(self, app_name: str, services: tuple, latest: bool = True) -> dict:
        """
        Arguments:
            app_name:
            services:
            latest:
        """

        register = _get_app_register(app_name=app_name, app_register=self._app_register)
        logs_buffer_file = register['log_buffer']
        log.debug(f"cubectl: configurator: creating logs buffer: {logs_buffer_file}")

        # getting status file
        status_file = Path(
            register['status_file']
        )
        status = SetupStatus(
            **_get_status(app_name=app_name, app_register=self._app_register)
        )
        # getting status file

        status.jobs = {
            str(uuid.uuid4()): {
                'get_logs': {'services': services, 'latest': latest, 'buffer_file': logs_buffer_file}
            }
        }

        logs_buffer_file_path = Path(logs_buffer_file)
        logs_buffer_file_path.parent.mkdir(parents=True, exist_ok=True)
        logs_buffer_file_path.touch()

        log.debug(f"cubectl: configurator: updating status file: {status_file}")
        with status_file.open('w') as new_status_file:
            yaml.dump(status.dict(), new_status_file)

        init_time_changed = logs_buffer_file_path.stat().st_mtime
        logs_result = None

        for _ in range(self._config.get('report_number_of_cycles', 5)):
            sleep(self._config.get('report_retry_wait_time', 1))
            last_time_changed = logs_buffer_file_path.stat().st_mtime
            if init_time_changed < last_time_changed:
                return read_yaml(logs_buffer_file_path)
        return {"services": "No logs received."}


def _get_register(app_register: str) -> list:
    """Returns whole register."""

    register_path = Path(app_register).resolve()
    if not register_path.is_file():
        raise ConfiguratorException('cubectl: No register found.')

    with register_path.open() as f:
        register: list = yaml.load(f, Loader=yaml.FullLoader)
        if not register:
            raise ConfiguratorException('cubectl: Register is empty.')

    return register


def _get_app_register(app_name: str, app_register: str) -> dict:
    """Returns info from register for specific app."""

    register_list = _get_register(app_register=app_register)
    if not register_list:
        raise ConfiguratorException(f'cubectl: configurator: no apps found in register')

    for app in register_list:
        if app['app_name'] == app_name:
            return app
    log.debug(f'cubectl: configurator: app: {app_name} not found.')
    return register_list[0]


def _get_status(app_name: str, app_register: str) -> dict:
    """Returns status object for specific app."""

    register = _get_app_register(app_name=app_name, app_register=app_register)
    status_file = Path(register['status_file'])

    with status_file.open() as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
    return result if result else dict()


def _get_all_allocated_ports_by_app(app_register: str) -> dict:
    """
    Returns dictionary with following format:
    {
        <app_name_0>: [<port>, ..., <port>],
        <app_name_1>: [<port>, ..., <port>],
        ...,
        <app_name_n>: [<port>, ..., <port>],
    }
    """
    register = _get_register(app_register=app_register)
    ports_by_app = dict()

    for app_name in (x['app_name'] for x in register):
        try:
            status = _get_status(app_name=app_name, app_register=app_register)
        except FileNotFoundError:
            continue
        services = status.get('services', [])
        ports = []
        for service in services:
            service_data = service['service_data']
            if not service_data:
                continue
            ports.append(service_data['port'])
        ports_by_app[app_name] = ports
    return ports_by_app
