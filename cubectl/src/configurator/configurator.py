import yaml
from pathlib import Path
import logging
from functools import reduce
from time import sleep

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

    def __init__(self, config: dict = None):
        if not config:
            config = dict()
        self._config = config
        self._app_register = config.get('applications_register', '/tmp/cubectl_application_register.yaml')

    def _get_register(self) -> dict:
        register = Path(self._app_register).resolve()
        if not register.is_file():
            raise ConfiguratorException('cubectl: No register found.')

        with register.open() as f:
            register_dict: dict = yaml.load(f, Loader=yaml.FullLoader)
            if not register_dict:
                raise ConfiguratorException('cubectl: Register is empty.')

        return register_dict

    def _get_app_register(self, app_name: str) -> dict:
        register_dict = self._get_register()

        try:
            return register_dict[app_name]
        except KeyError:
            return list(register_dict.values())[0]

    def _get_all_allocated_ports_by_app(self):
        register = self._get_register()
        ports_by_app = dict()

        for app_name in register.keys():
            try:
                status = self._get_status(app_name)
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

    def _get_status(self, app_name: str):
        register = self._get_app_register(app_name=app_name)
        status_file = Path(register['status_file'])

        with status_file.open() as f:
            result = yaml.load(f, Loader=yaml.FullLoader)
        return result if result else dict()

    def _assign_ports_to_services(self, status):
        ports_by_app = self._get_all_allocated_ports_by_app()
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
        status_object = self._assign_ports_to_services(status=status_object)

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

    def start(self, app_name: str, services: tuple):
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.started
        )

    def stop(self, app_name: str, services: tuple):
        self._change_process_state(
            app_name=app_name, services=services, state=ProcessState.stopped
        )

    def restart(self, app_name: str = None, services: tuple = tuple()):
        app_name = app_name + '_' if app_name else ''
        register = self._get_app_register(app_name=app_name)
        status_file = Path(
            register['status_file']
        )
        status = SetupStatus(
            **self._get_status(app_name=app_name)
        )

        status.jobs = {
            'restart': ','.join(services)
        }
        with status_file.open('w') as new_status_file:
            yaml.dump(status.dict(), new_status_file)

    def status(self, app_name: str = None, report_location: str = '/tmp'):
        """
        Arguments:
            app_name:
            report_location: location of file with results

        """

        app_name = app_name + '_' if app_name else ''
        report_file = f'{report_location}/{app_name}status_report.yaml'.replace('//', '/')
        register = self._get_app_register(app_name=app_name)
        status_file = Path(
            register['status_file']
        )
        status = SetupStatus(
            **self._get_status(app_name=app_name)
        )

        status.jobs = {
            'get_report': report_file
        }
        report_file_path = Path(report_file)
        report_file_path.touch()

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
