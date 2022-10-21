from pydantic import BaseModel
from enum import Enum


__all__ = [
    "Command",
    "ConfiguratorRequest"
]


class Command(str, Enum):
    start = 'START'
    stop = 'STOP'
    restart = 'RESTART'
    status = 'STATUS'
    logs = 'LOGS'
    get_log_level = 'GET_LOG_LEVEL'
    set_log_level = 'SET_LOG_LEVEL'

    generate_nginx_conf = 'GENERATE_NGINX_CONF'


class ConfiguratorRequest(BaseModel):
    services: list[str]
    command: str
