from pydantic import BaseModel
from typing import Optional
from enum import Enum

from cubectl.src.models import InitProcessConfig


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
    failed_to_start = 'FAILED_TO_START'


class SystemData(BaseModel):
    pid: Optional[int]
    state: ProcessState
    error_code: Optional[int]
    started_at: Optional[str]

    class Config:  
        use_enum_values = True


class ServiceData(BaseModel):
    port: Optional[int]
    nginx_config: Optional[str]


class ProcessStatus(BaseModel):
    system_data: SystemData
    service_data: Optional[ServiceData]
    init_config: InitProcessConfig


JobName = str


class SetupStatus(BaseModel):
    jobs: dict[JobName, object] = dict()
    services: list[ProcessStatus] = list()
