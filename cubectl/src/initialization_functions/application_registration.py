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
        register_path: str,
        temp_files_dir: str,
        reinit: bool = False,
):
    """Writes new application to register.yaml file."""

    init_config = InitFileModel(**init_config)
    app_name = init_config.installation_name
    register_path = Path(register_path)

    temp_files = {
        'status_file': f'{temp_files_dir}/{app_name}/status.yaml',
        'status_report': f'{temp_files_dir}/{app_name}/status_report.yaml',
        'log_buffer': f'{temp_files_dir}/{app_name}/log_buffer.yaml',
    }
    status_file = temp_files['status_file']

    entity = RegisterEntity(
        app_name=app_name,
        **temp_files,
    )

    register_from_file = None

    if register_path.is_file():
        with register_path.open() as f:
            register_from_file = yaml.load(f, Loader=yaml.FullLoader)
    else:
        register_dir = register_path.parent
        register_dir.mkdir(parents=True, exist_ok=True)

    register = register_from_file if register_from_file else list()
    registered_apps = [x['app_name'] for x in register]

    if app_name in registered_apps:
        if reinit:
            log.debug(f'cubectl: application_registration: application {app_name} '
                      f'overriden in register')
            register = [x for x in register if x['app_name'] != app_name]
        else:
            message = (f'cubectl: application_registration: application {app_name} '
                       f'was not overriden in register, because override is False'
                       )
            log.error(message)
            raise ValueError(message)

    register.append(entity.dict())

    with register_path.open('w') as f:
        yaml.dump(register, f, Dumper=yaml.Dumper)
        log.debug(f'cubectl: application_registration: status_file: {status_file}, registered in: {register_path}')
    return temp_files


def unregister_application(
        app_name: str,
        register_path: str,
):
    """Writes new application to register.yaml file."""

    register_path = Path(register_path)

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

    if process_init_config.log:
        resolved_log_path = resolve_path(
           root_dir=root_dir, file_path=process_init_config.log, return_dir=False
        )

        if Path(resolved_log_path).is_file():
            process_init_config.log = str(Path(resolved_log_path))
        else:
            log.warning(f'cubectl: application_registration: '
                        f'log file {resolved_log_path} not found and replaced by None'
                        )
            process_init_config.log = None

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
