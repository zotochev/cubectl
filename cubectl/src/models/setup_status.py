from pydantic import BaseModel
from typing import Optional
from enum import Enum

from src.models import InitProcessConfig


__all__ = [
    "ProcessState",
    "SystemData",
    "ServiceData",
    "ProcessStatus",
    "SetupStatus"
]


class ProcessState(str, Enum):
    stopped = 'STOPPED'
    started = 'STARTED'
    failed_start_loop = 'FAILED_START_LOOP'


class SystemData(BaseModel):
    pid: Optional[int]
    state: ProcessState
    error_code: Optional[int]

    class Config:  
        use_enum_values = True


class ServiceData(BaseModel):
    port: Optional[int]
    nginx_config: Optional[str]


class ProcessStatus(BaseModel):
    system_data: SystemData
    service_data: Optional[ServiceData]
    init_config: InitProcessConfig


class SetupStatus(BaseModel):
    services: Optional[list[ProcessStatus]]
