import os
import io
from subprocess import Popen
from typing import Optional
from time import sleep
from datetime import datetime
import logging
from pathlib import Path

import dotenv

from src.models import InitProcessConfig
from src.models import ProcessState
from src.models import ProcessStatus
from src.models import SystemData
from src.models import ServiceData


OS_OPERATIONS_DELAY = 0.1
log = logging.getLogger(__file__)


class ServiceProcess:
    def __init__(self, init_config: dict):
        self._init_config = InitProcessConfig(**init_config)
        self._start_up_command: list[str] = self._create_start_up_command()
        self._process: Optional[Popen] = None
        self._state = ProcessState.stopped
        self._process_started_at = None
        self._process_stopped_at = None

        self._resolve_env()

        if self._init_config.service:
            # todo
            #   choose port
            #   create nginx config
            pass

    def _create_start_up_command(self):
        if self._init_config.command is not None:
            log.warning(
                f'{__file__}: Use executor, arguments '
                f'and file fields instead command.'
            )
            return self._init_config.command.split()
        else:
            executor = self._init_config.executor
            file = self._init_config.file
            args = self._init_config.arguments
            args = ' '.join([f'{k} {v}' for k, v in args.items()])
            return [x for x in f'{executor} {file} {args}'.split() if x]

    def start(self):
        self._check_process()
        if self._state is ProcessState.started:
            return

        self._process = Popen(
            self._start_up_command,
            env=self._resolve_env()
        )

        self._check_process()
        if self._state is not ProcessState.started:
            self._state = ProcessState.failed_start_loop
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
        return self._process.pid

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._init_config.name

    def is_service(self):
        return self._init_config.service

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
        )

    def _status_collect_service_data(self) -> ServiceData:
        """
        port: Optional[int]
        nginx_config: Optional[str]
        """
        _ = self

        return ServiceData(
            port=123456789,
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
            if self._state is not ProcessState.failed_start_loop:
                self._state = ProcessState.stopped
        else:
            self._state = ProcessState.started
        return error_code

    def stop(self):
        if self.state is not ProcessState.stopped:
            if self._process is not None:
                self._process.kill()
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

        # if self._init_config.dotenv:
        #     self._apply_env_dotenv()
        if self._init_config.env_files:
            self._apply_env_files()

        result = os.environ.copy()

        if self._init_config.environment:
            for k, v in self._init_config.environment.items():
                result[k] = v
        return result

    def _compare_status_init_config(self, desired_status: InitProcessConfig) -> bool:
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
        current_status = self._init_config.copy().dict()
        not_found = '__not_found__'

        for key, value in desired_status.items():
            current_value = current_status.get(key, not_found)
            if value != current_value and current_value != not_found:
                return False
        return True

    def _make_follow_updated_init(self, desired_status: InitProcessConfig):

        desired_status = desired_status.dict()
        current_status = self._init_config.copy().dict()
        not_changed = {k: v for k, v in current_status.items() if k not in desired_status}

        self._init_config = InitProcessConfig(
            **desired_status,
            **not_changed       # note: ???
        )
        self._start_up_command = self._create_start_up_command()

    def _compare_status_service_data(self, desired_status: ServiceData) -> bool:
        """
        'service_data': {'nginx_config': '', 'port': 123456789},
        """
        _ = self
        return True

    def _make_follow_service_data(self, desired_status: ServiceData):
        pass

    def _compare_status_system_data(self, desired_status: SystemData) -> bool:
        """
        'system_data': {'error_code': None, 'pid': 363868, 'state': 'STARTED'}
        """
        return desired_status.state is self.state

    def _make_to_follow_state(self, state: ProcessState):
        factory = {
            ProcessState.started: self.start,
            ProcessState.stopped: self.stop
        }
        factory[state]()

    def _make_to_follow_system_data(self, desired_status: SystemData):
        """
        Handle restart in this function if needed
        """
        self._make_to_follow_state(desired_status.state)

    def apply_status(self, desired_status: ProcessStatus):
        to_restart = False

        if not self._compare_status_init_config(desired_status.init_config):
            to_restart = True
            self._make_follow_updated_init(desired_status.init_config)

        if not self._compare_status_service_data(desired_status.service_data):
            to_restart = True
            self._make_follow_service_data(desired_status.service_data)

        if to_restart:
            self.restart()

        if not self._compare_status_system_data(desired_status.system_data):
            # usually no need to restart
            self._make_to_follow_system_data(desired_status.system_data)

    def get_logs(self):
        raise NotImplemented('service_process.py')

    def get_log_level(self):
        raise NotImplemented('service_process.py')

    def set_log_level(self):
        raise NotImplemented('service_process.py')

    def generate_nginx_conf(self):
        raise NotImplemented('service_process.py')

    def _check_requirements(self):
        raise NotImplemented('service_process.py')

    def _set_env(self):
        raise NotImplemented('service_process.py')

    def _check_external_resources(self):
        raise NotImplemented('service_process.py')


def main():
    pass


if __name__ == "__main__":
    main()
