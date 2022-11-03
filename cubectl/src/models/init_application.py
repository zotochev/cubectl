from typing import Optional
from pydantic import BaseModel, validator

from cubectl.src.models.init_process import InitProcessConfig


__all__ = [
    "RegisterEntity",
    "InitFileModel",
]


class RegisterEntity(BaseModel):
    app_name: str
    status_file: str
    status_report: Optional[str]
    log_buffer: Optional[str]


class InitFileModel(BaseModel):
    installation_name: str
    # status_file_dir: str = '/tmp'
    set_up_commands: list = []
    tear_down_commands: list = []
    root_dir: Optional[str]
    processes: list[InitProcessConfig] = []
