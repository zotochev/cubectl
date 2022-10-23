from typing import Optional
from pydantic import BaseModel

from src.models.init_process import InitProcessConfig


__all__ = [
    "RegisterEntity",
    "InitFileModel",
]


class RegisterEntity(BaseModel):
    status_file: str = '/tmp/default_name_status_file.yaml'


class InitFileModel(BaseModel):
    installation_name: str = 'default_name'
    status_file: str = '/tmp/default_status_file.yaml'
    set_up_commands: list = []
    tear_down_commands: list = []
    root_dir: Optional[str]
    processes: list[InitProcessConfig] = []
