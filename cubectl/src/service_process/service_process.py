import os
import io
from subprocess import Popen
from typing import Optional
from time import sleep
from datetime import datetime
import logging
from pathlib import Path

import dotenv

from cubectl.src.models import InitProcessConfig
from cubectl.src.models import ProcessState
from cubectl.src.models import ProcessStatus
from cubectl.src.models import SystemData
from cubectl.src.models import ServiceData
from cubectl.src.utils import LogReaderProtocol, LogReader


OS_OPERATIONS_DELAY = 0.1
log = logging.getLogger(__file__)


class ServiceProcessException(Exception):
    pass


class ServiceProcessNoRetriesException(ServiceProcessException):
    pass


class ServiceProcess:
    def __init__(self, init_config: dict, number_of_start_retries: int = 10):
        self._init_config = InitProcessConfig(**init_config)
        self._start_up_command: list[str] = _create_start_up_command(
            executor=self._init_config.executor,
            file=self._init_config.file,
            args=self._init_config.arguments
        )
        self._process: Optional[Popen] = None
        self._state = ProcessState.stopped
        self._process_started_at = None
        self._process_stopped_at = None

        self._resolve_env()

        self._port = None
        if self._init_config.service:
            if self._init_config.port:
                self._port = self._init_config.port
        self._number_of_start_retries = number_of_start_retries
        self._number_of_start_retries_left = number_of_start_retries
        self._log_reader: LogReaderProtocol = LogReader(self._init_config.log)

    def start(self):
        self._check_process()
        if self._state is ProcessState.started:
            return
        if self._state is ProcessState.failed_to_start:
            log.warning(
                f'cubectl: ServiceProcess: {self.name} is in {self._state} state. '
                f'Try to restart before process'
            )
            return

        self._process = Popen(
            self._start_up_command,
            env=self._resolve_env()
        )

        self._check_process()
        if self._state is not ProcessState.started:
            self._state = ProcessState.failed_start_loop
            try:
                self._decrement_retries()
            except ServiceProcessNoRetriesException:
                self._state = ProcessState.failed_to_start
        else:
            self._process_started_at = datetime.now()

    def status(self) -> ProcessStatus:
        """
        system_data: SystemData
        service_data: Optional[ServiceData]
        init_config: InitProcessConfig
        """

        return ProcessStatus(
            system_data=self._status_collect_system_data(),
            service_data=self._status_collect_service_data(),
            init_config=self._init_config,
        )

    @property
    def pid(self) -> int:
        return self._process.pid if self._process else None

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._init_config.name

    def is_service(self):
        return self._init_config.service

    def is_fail_restart_loop(self) -> bool:
        return self.state is ProcessState.failed_start_loop

    def _reset_process_start_retries(self):
        self._number_of_start_retries_left = self._number_of_start_retries

    def _decrement_retries(self):
        if self._number_of_start_retries_left == 0:
            raise ServiceProcessNoRetriesException(
                'cubectl: ServiceProces: no start up retries left.'
            )
        self._number_of_start_retries_left -= 1

    def _status_collect_system_data(self) -> SystemData:
        """
        pid: Optional[int]
        state: ProcessState
        error_code: Optional[int]
        """
        _ = self
        error_code = self._check_process()

        return SystemData(
            pid=self.pid,
            state=self._state,
            error_code=error_code,
            started_at=str(self._process_started_at),
        )

    def _status_collect_service_data(self) -> ServiceData:
        """
        port: Optional[int]
        nginx_config: Optional[str]
        """
        _ = self

        return ServiceData(
            port=self._port,
            nginx_config='',
        )

    def _check_process(self):
        error_code = -555
        sleep(OS_OPERATIONS_DELAY)

        if self._process is not None:
            error_code = self._process.poll()

        if error_code is not None:
            self._process_stopped_at = datetime.now()

            self._process_started_at = None
            if (self._state is not ProcessState.failed_start_loop
                    and self._state is not ProcessState.failed_to_start):
                self._state = ProcessState.stopped
            elif self.state is ProcessState.failed_start_loop and self._number_of_start_retries_left == 0:
                self._state = ProcessState.failed_to_start
        else:
            self._state = ProcessState.started
        return error_code

    def stop(self):
        self._reset_process_start_retries()

        if self.state is not ProcessState.stopped:
            if self._process is not None:
                self._process.kill()
        if (self.state is ProcessState.failed_start_loop
                or self.state is ProcessState.failed_to_start):
            self._state = ProcessState.stopped
        self._check_process()

    def restart(self):
        self.stop()
        self.start()

    def _apply_env_files(self):
        env_files = self._init_config.env_files
        if self._init_config.dotenv:
            env_files = [
                *env_files,
                str(Path(Path(self._init_config.file).parent, '.env'))
            ]
        env_vars = ''

        for env_file in env_files:
            try:
                with open(env_file) as f:
                    env_vars += f.read() + '\n'
            except Exception as e:
                log.error(str(e))

        variables_stream = io.StringIO(env_vars)
        dotenv.load_dotenv(stream=variables_stream)

    def _resolve_env(self) -> dict:
        """
        Add env variables from env files.

        get env vars from:
            'dotenv': True,
            'env_files': [],
            'environment': {},

        and set them up to result dict
        """

        if self._init_config.env_files:
            self._apply_env_files()

        result = os.environ.copy()

        if self._init_config.environment:
            for k, v in self._init_config.environment.items():
                result[k] = v
        return result

    def _make_follow_updated_init(self, desired_status: InitProcessConfig):

        desired_status = desired_status.dict()
        current_status = self._init_config.copy().dict()
        not_changed = {k: v for k, v in current_status.items() if k not in desired_status}

        self._init_config = InitProcessConfig(
            **desired_status,
            **not_changed,
        )
        self._start_up_command: list[str] = _create_start_up_command(
            executor=self._init_config.executor,
            file=self._init_config.file,
            args=self._init_config.arguments
        )

    def _compare_status_service_data(self, desired_status: ServiceData) -> bool:
        """
        'service_data': {'nginx_config': '', 'port': 123456789},
        """
        _ = self
        return self._port == desired_status.port

    def _make_follow_service_data(self, desired_status: ServiceData):
        self._port = desired_status.port

    def _compare_status_system_data(self, desired_status: SystemData) -> bool:
        """
        'system_data': {'error_code': None, 'pid': 363868, 'state': 'STARTED'}
        """
        return desired_status.state is self.state

    def _make_to_follow_state(self, state: ProcessState):
        factory = {
            ProcessState.started: self.start,
            ProcessState.stopped: self.stop,
        }
        factory[state]()

    def _make_to_follow_system_data(self, desired_status: SystemData):
        """
        Handle restart in this function if needed
        """
        self._make_to_follow_state(desired_status.state)

    def apply_status(self, desired_status: ProcessStatus):
        to_restart = False

        if not _compare_status_init_config(
            current_status=self._init_config,
            desired_status=desired_status.init_config
        ):
            to_restart = True
            self._make_follow_updated_init(desired_status.init_config)

        if self.is_service() and not self._compare_status_service_data(desired_status.service_data):
            to_restart = True
            self._make_follow_service_data(desired_status.service_data)

        if to_restart:
            self.restart()

        if not self._compare_status_system_data(desired_status.system_data):
            # usually no need to restart
            self._make_to_follow_system_data(desired_status.system_data)

    def get_logs(self, latest: bool = True):
        try:
            if latest:
                return self._log_reader.get_latest_log()
            return self._log_reader.get_log()
        except Exception as e:
            log.critical(f'cubectl: service_process: log_reader failed with error: {e}')
            return ''

    def get_log_level(self):
        raise NotImplemented('service_process.py')

    def set_log_level(self):
        raise NotImplemented('service_process.py')


def _create_start_up_command(executor: str, file: str, args: dict):
    args = ' '.join([f'{k} {v}' for k, v in args.items()])
    return [x for x in f'{executor} {file} {args}'.split() if x]


def _compare_status_init_config(current_status: InitProcessConfig, desired_status: InitProcessConfig) -> bool:
    """
    Compares desired_status with current state of process and if not
    replaces init file with new one.

    todo:
        compare env (also check inside files)

    Returns:
        True if desired_status is same as current
        False in other case
    """

    desired_status = desired_status.dict()
    # current_status = self._init_config.copy().dict()
    current_status = current_status.dict()
    not_found = '__not_found__'

    for key, value in desired_status.items():
        current_value = current_status.get(key, not_found)
        if value != current_value and current_value != not_found:
            return False
    return True


def main():
    pass


if __name__ == "__main__":
    main()
