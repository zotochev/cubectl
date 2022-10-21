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

        # self.start()

    def start(self):
        self._check_process()
        if self._state is ProcessState.started:
            return

        self._process = Popen(self._init_config.command.split())

        self._check_process()
        if self._state is not ProcessState.started:
            self._state = ProcessState.failed_start_loop
            # raise Exception('Process failed to start')

    def status(self) -> ProcessStatus:
        """
        system_data: SystemData
        service_data: Optional[ServiceData]
        init_config: InitProcessConfig
        """

        error_code = self._check_process()

        # return ProcessStatus(
        #     state=self._state,
        #     error_code=error_code,
        #     pid=self._process.pid if self._process is not None else None,
        #     init_config=self._init_config
        # )
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

        return SystemData(
            pid=self.pid,
            state=self._state,
            error_code=self._check_process(),
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

    def _compare_status(self, desired_status: dict):
        raise NotImplemented('service_process.py')

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
