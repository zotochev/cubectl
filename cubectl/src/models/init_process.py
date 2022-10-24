from typing import Optional
from pydantic import BaseModel


__all__ = [
    "InitProcessConfig",
]


class InitProcessConfig(BaseModel):
    name: Optional[str]
    command: Optional[str]                # deprecated

    executor: str = ''
    file: Optional[str]                   # cubectl/tests/example_services/example_service_0.py'
    arguments: Optional[dict]              # {'--name': 'new_name'}

    environment: dict[str, str] = dict()  # list of env variables
    env_files: list[str] = list()         # list of env files
    dotenv: bool = True                   # if true (default true) tries to load .env file near command file
    service: bool = True                  # if true (default false) assigns port and nginx config
