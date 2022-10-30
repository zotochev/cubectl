import yaml
from pathlib import Path
import logging

from cubectl.src.utils import resolve_path

from cubectl.src.models import (
    RegisterEntity,
    InitFileModel,
    SetupStatus,
    ProcessStatus,
    InitProcessConfig,
    ServiceData,
    SystemData,
    ProcessState
)


__all__ = [
    "register_application",
    "create_status_object",
]

log = logging.getLogger(__file__)


def register_application(
        init_config: dict,
        status_file: str,
        register_path: str = '/tmp/cubectl_applications_register.yaml'
):
    """Writes new application to register.yaml file."""

    init_config = InitFileModel(**init_config)
    register_path = Path(register_path)
    entity = RegisterEntity(
        status_file=status_file,
    )

    register_from_file = None

    if register_path.is_file():
        with register_path.open() as f:
            register_from_file = yaml.load(f, Loader=yaml.FullLoader)

    register = register_from_file if register_from_file else dict()
    register[init_config.installation_name] = entity.dict()

    with register_path.open('w') as f:
        yaml.dump(register, f, Dumper=yaml.Dumper)
        log.warning(f'cubectl: application_registration: status_file: {status_file}, registered in: {register_path}')


def init_service_status(root_dir, process_init_config: InitProcessConfig):
    """
    Arguments:
        root_dir: path string for resolving path arguments for
            lauching commands and env files.
        process_init_config:
            class InitProcessConfig(BaseModel):
                name: Optional[str]
                command: Optional[str]                # deprecated

                executor: Optional[str] = 'python'
                file: Optional[str]                   # cubectl/tests/example_services/example_service_0.py'
                arguments: Optional[dict]              # {'--name': 'new_name'}

                environment: dict[str, str] = dict()  # list of env variables
                env_files: list[str] = list()         # list of env files
                dotenv: bool = True                   # if true (default true) tries to load .env file near command file
                service: bool = True                  # if true (default false) assigns port and nginx config
    """
    process_name = process_init_config.name

    file = resolve_path(
        root_dir=root_dir, file_path=process_init_config.file, return_dir=False
    )

    if not Path(file).is_file():
        _message = (
            f'cubectl: application_registration: command for process "{process_name}": \n'
            f'\t{process_init_config.executor} {file}'
        )
        log.error(_message)
        raise FileNotFoundError(_message)
    process_init_config.file = file
    env_files = process_init_config.env_files
    process_init_config.env_files = [
        resolve_path(root_dir=root_dir, file_path=x, return_dir=False)
        for x in env_files
    ]

    system_data = SystemData(
        state=ProcessState.stopped
    )
    service_data = None
    if process_init_config.service:
        service_data = ServiceData(port=None)

    return ProcessStatus(
        init_config=process_init_config,
        service_data=service_data,
        system_data=system_data,
    )


def init_services_status(init_config: InitFileModel) -> list[ProcessStatus]:
    services = list()

    for process in init_config.processes:
        services.append(
            init_service_status(
                root_dir=init_config.root_dir,
                process_init_config=process
            )
        )
    return services


def init_jobs(init_config: InitFileModel):
    _ = init_config
    return dict()


def create_status_object(init_config: dict) -> SetupStatus:
    """
    class InitFileModel(BaseModel):
        installation_name: str = 'default_name'
        status_file: str = '/tmp/default_status_file.yaml'
        set_up_commands: list = []
        tear_down_commands: list = []
        root_dir: Optional[str]
        processes: list[InitProcessConfig] = []

    class ProcessStatus(BaseModel):
        system_data: SystemData
        service_data: Optional[ServiceData]
        init_config: InitProcessConfig

    class SetupStatus(BaseModel):
        jobs: dict[JobName, InitProcessConfig] = dict()
        services: list[ProcessStatus] = list()
    """

    init_config = InitFileModel(**init_config)
    status = SetupStatus(
        jobs=init_jobs(init_config),
        services=init_services_status(init_config)
    )

    return status
