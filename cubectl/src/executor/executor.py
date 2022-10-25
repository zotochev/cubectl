import logging
from pathlib import Path
import yaml
from time import sleep
from typing import Optional

from src.service_process import ServiceProcess
from src.models.setup_status import ProcessStatus, SetupStatus


log = logging.getLogger(__file__)


class Executor:
    """
    Starts up processed
    Monitors processes state
    Applies changes from state file
    """

    def __init__(self, status_file: str):
        self._status_file = Path(status_file).resolve(strict=True)
        self._validate_status_file(self._status_file)
        self._status_file_last_change = int(self._status_file.stat().st_mtime)
        self._processes = self._setup_processes()

    @staticmethod
    def _validate_status_file(status_file: Path):
        with status_file.open() as sf:
            status_file_dict = yaml.load(sf, Loader=yaml.FullLoader)
            if 'jobs' not in status_file_dict and 'services' not in status_file_dict:
                raise TypeError(
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

    def _do_jobs(self, jobs: dict):
        factory = {
            'get_report': self._send_report,
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

    def _get_status(self):
        with self._status_file.open() as f:
            status = yaml.load(f, Loader=yaml.FullLoader)
        return status

    def _is_status_changed(self):
        last_change = int(self._status_file.stat().st_mtime)

        if last_change != self._status_file_last_change:
            self._status_file_last_change = last_change
            return True

        return False

    def process(self, cycle_period: int = 1):
        while True:
            if self._is_status_changed():
                self._update_processes()

            sleep(cycle_period)
