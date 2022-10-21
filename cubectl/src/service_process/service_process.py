import os
from subprocess import Popen
from typing import Optional
from time import sleep

from src.models import InitProcessConfig
from src.models import ProcessState
from src.models import ProcessStatus
from src.models import SystemData
from src.models import ServiceData


WAIT_TIME_TO_START_UP = 0.1


class ServiceProcess:
    def __init__(self, init_config: dict):
        self._init_config = InitProcessConfig(**init_config)
        self._process: Optional[Popen] = None
        self._state = ProcessState.stopped

        if self._init_config.service:
            # todo
            pass

    def start(self):
        self._check_process()
        if self._state is ProcessState.started:
            return

        self._process = Popen(
            self._init_config.command.split(),
            env=self._resolve_env()
        )

        self._check_process()
        if self._state is not ProcessState.started:
            self._state = ProcessState.failed_start_loop

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
        sleep(WAIT_TIME_TO_START_UP)

        if self._process is not None:
            error_code = self._process.poll()

        if error_code is not None:
            if self._state is not ProcessState.failed_start_loop:
                self._state = ProcessState.stopped
        else:
            self._state = ProcessState.started
        return error_code

    def stop(self):
        self._process.kill()
        self._check_process()

    def restart(self):
        self.stop()
        self.start()

    def _resolve_env(self) -> dict:
        """
        Add env variables from env files.

        get env vars from:
            'dotenv': True,
            'env_files': [],
            'environment': {},

        and set them up to result dict
        """

        _ = self
        result = os.environ.copy()
        return result

    def _compare_status_init_config(self, desired_status: InitProcessConfig) -> bool:
        """
        Compares desired_status with current state of process and if not
        replaces init file with new one.

        Returns:
            True if desired_status is same as current
            False in other case
        """

        # todo compare env (also files)
        desired_status = desired_status.dict()
        current_status = self._init_config.copy().dict()
        not_found = '__not_found__'

        for key, value in desired_status.items():
            current_value = current_status.get(key, not_found)
            if value != current_value and current_value != not_found:
                not_changed = {k: v for k, v in current_value if k not in desired_status}
                self._init_config = InitProcessConfig(
                    **desired_status,
                    **not_changed       # note: ???
                )
                return False
        return True

    def _compare_status_service_data(self, desired_status: ServiceData) -> bool:
        """
        'service_data': {'nginx_config': '', 'port': 123456789},
        """
        _ = self
        return True

    def _compare_status_system_data(self, desired_status: SystemData) -> bool:
        """
        'system_data': {'error_code': None, 'pid': 363868, 'state': 'STARTED'}
        """
        return desired_status.state is self.state

    def _compare_status(self, desired_status: ProcessStatus):
        if not all((
            self._compare_status_init_config(desired_status=desired_status.init_config),
            self._compare_status_system_data(desired_status=desired_status.system_data),
            self._compare_status_service_data(desired_status=desired_status.service_data),
        )):
            pass

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
