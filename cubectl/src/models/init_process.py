from typing import Optional
from pydantic import BaseModel


__all__ = [
    "InitProcessConfig",
]


class InitProcessConfig(BaseModel):
    name: str

    executor: str
    file: str                             # cubectl/tests/example_services/example_service_0.py'
    arguments: dict = dict()              # {'--name': 'new_name'}

    environment: dict[str, str] = dict()  # list of env variables
    env_files: list[str] = list()         # list of env files
    dotenv: bool = True                   # if true (default true) tries to load .env file near command file
    service: bool = True                  # if true (default false) assigns port and nginx config
    port: Optional[int]
    log: Optional[str]                    # location of log-file
