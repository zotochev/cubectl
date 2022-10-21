from pydantic import BaseModel
from typing import Optional

from src.models.setup_status import ProcessState
from src.models.init_process import InitProcessConfig


# __all__ = [
#     "ProcessStatus",
# ]
#
#
# class ProcessStatus(BaseModel):
#     state: ProcessState
#     pid: Optional[int]
#     init_config: InitProcessConfig
#     error_code: Optional[int]
#
#     class Config:
#         use_enum_values = True
