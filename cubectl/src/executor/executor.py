import logging
from pathlib import Path
import yaml
from time import sleep
from typing import Optional

from cubectl.src.service_process import ServiceProcess
from cubectl.src.models.setup_status import ProcessStatus
from cubectl.src.utils import Messanger


log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)


class ExecutorException(Exception):
    pass


class Executor:
    """
    Starts up processed
    Monitors processes state
    Applies changes from state file
    """

    def __init__(self, status_file: str, meta_info: Optional[dict] = None):
        """
        Arguments:
            status_file:
            meta_info:
                Info for reports and messaging as additional information.
                Used as it is not expected to have any specific keys/values.
        """

        self._status_file = Path(status_file).resolve(strict=True)
        self._validate_status_file(self._status_file)

        self._status_file_last_change = int(self._status_file.stat().st_mtime)
        self._processes = self._setup_processes()
        self._messanger: Optional[Messanger] = None
        self._meta_info = meta_info

    @staticmethod
    def _validate_status_file(status_file: Path):
        with status_file.open() as sf:
            status_file_dict = yaml.load(sf, Loader=yaml.FullLoader)
            if 'jobs' not in status_file_dict and 'services' not in status_file_dict:
                raise ExecutorException(
                    f'cubectl: Executor: invalid status file structure: '
                    f'{status_file_dict.keys()}. For: {status_file}'
                )

    def _setup_processes(self) -> list:
        status = self._get_status()
        processes = []

        for process_status in status.get('services', []):
            init_config = process_status['init_config']
            process = ServiceProcess(init_config=init_config)
            processes.append(process)
        return processes

    def _get_process_by_name(self, name) -> Optional[ServiceProcess]:
        for process in self._processes:
            if process.name == name:
                return process
        return None

    def _send_report(self, report_file: str):
        report = dict()

        for process in self._processes:
            process: ServiceProcess
            report[process.name] = process.status().dict()

        try:
            with Path(report_file).open('w') as f:
                yaml.dump(report, f)
        except Exception as e:
            log.error(
                f'cubectl: executor: failed to save report: {report_file} '
                f'with error: {e}.'
            )

    def restart(self, services: str):
        services = [x for x in services.split(',') if x]
        for process in self._processes:
            process: ServiceProcess
            if process.name in services or not services:
                process.restart()

    def _stop_all_processes(self):
        for process in self._processes:
            process: ServiceProcess
            process.stop()

    def _do_jobs(self, jobs: dict):
        factory = {
            'get_report': self._send_report,
            'restart': self.restart,
        }

        for method in factory:
            if method in jobs:
                factory[method](jobs[method])

    def _update_processes(self):
        status = self._get_status()

        self._do_jobs(status.get('jobs', {}))

        for process_status in status.get('services', []):
            init_config = process_status['init_config']
            process_name = init_config['name']

            process = self._get_process_by_name(name=process_name)
            if not process:
                log.warning(
                    f'cubectrl: executor: process {process_name} not found'
                )
                continue
            process_status = ProcessStatus(**process_status)
            process.apply_status(process_status)

    def _health_check(self):
        for process in self._processes:
            if process.is_fail_restart_loop():
                self._message_process_status(process=process)

    def _get_status(self):
        with self._status_file.open() as f:
            status = yaml.load(f, Loader=yaml.FullLoader)
        return status

    def _is_status_file_changed(self):
        last_change = int(self._status_file.stat().st_mtime)

        if last_change != self._status_file_last_change:
            self._status_file_last_change = last_change
            return True

        return False

    def process(self, cycle_period: int = 1):
        first_cycle = True

        try:
            while True:
                if self._is_status_file_changed() or first_cycle or True:
                    first_cycle = False
                    self._update_processes()

                self._health_check()

                sleep(cycle_period)
        except KeyboardInterrupt:
            self._stop_all_processes()

    def add_messanger(self, messanger: Messanger):
        self._messanger = messanger

    def _message_process_status(self, process: ServiceProcess, note: str = None):
        if not self._messanger:
            return

        message = {
            'process_name': process.name,
            'state': process.state,
            'note': note,
            'meta_info': self._meta_info,
        }
        self._messanger.post(message=message)
