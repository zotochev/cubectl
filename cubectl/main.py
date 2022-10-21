from time import sleep

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
    command: Path
    environment: dict[str, str] = dict()  # list of env variables
    env_files: list[str] = list()         # list of env files
    dotenv: bool = True                   # if true (default true) tries to load .env file near command file
    service: bool = True                  # if true (default false) assigns port and nginx config
    """
    init_config = {
        'name': 'test_process',
        # 'command': 'python cubectl/src/example_services/example_service_0.py',
        'command': 'python src/example_services/example_service_0.py',
    }
    # pr = ServiceProcess(init_config=init_config)
    # print(pr.status().dict())
    # sleep(1)
    # pr.restart()
    # sleep(1)
    # print(pr.status().dict())
    # sleep(3)
    from subprocess import Popen

    a = Popen(init_config['command'].split())
    sleep(0.1)
    print(a.poll())


if __name__ == '__main__':
    main()
