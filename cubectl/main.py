from time import sleep
import dotenv

from cubectl.src.service_process.service_process import ServiceProcess
from cubectl.src.executor.executor import Executor
from cubectl.src.configurator.configurator import Configurator


def configure(services: list):
    c = Configurator(services=services, status_file='')


def observe(check_period: int = 1):
    e = Executor()

    while True:
        status_file = dict()
        e.update(status_file=status_file)

        sleep(check_period)


def main():
    """
    name: Optional[str]
    command: str
    environment: dict[str, str] = dict()  # list of env variables
    env_files: list[str] = list()         # list of env files
    dotenv: bool = True                   # if true (default true) tries to load .env file near command file
    service: bool = True                  # if true (default false) assigns port and nginx config
    """

    init_config_ok = {
        'name': 'test_process',
        # 'command': 'python cubectl/tests/example_services/example_service_0.py',

        'executor': 'python',
        'file': 'cubectl/tests/example_services/example_service_0.py',
        'arguments': {'--name': 'new_name'},
        'dotenv': True,
        'environment': {'TWO': 'TWO2'},
        'env_files': ['cubectl/tests/example_services/environments/local.env']
    }

    pr = ServiceProcess(init_config=init_config_ok)
    pr.start()
    sleep(5)
    pr.stop()


if __name__ == '__main__':
    main()
