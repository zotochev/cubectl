import yaml
from pathlib import Path

from src.models import RegisterEntity, InitFileModel


__all__ = [
    "register_application",
    "create_status_file",
]


def register_application(
        init_config: InitFileModel,
        register_path: str = '/tmp/cubectl_applications_register.yaml'
):
    register_path = Path(register_path)
    entity = RegisterEntity(
        status_file=init_config.status_file,
    )

    register_from_file = None

    if register_path.is_file():
        with register_path.open() as f:
            register_from_file = yaml.load(f, Loader=yaml.FullLoader)

    register = register_from_file if register_from_file else dict()
    register[init_config.installation_name] = entity.dict()

    with register_path.open('w') as f:
        yaml.dump(register, f, Dumper=yaml.Dumper)


def create_status_file(init_config: InitFileModel):
    pass
