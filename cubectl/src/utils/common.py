import yaml
from pathlib import Path
from functools import cache
import pydantic
from typing import Optional


__all__ = [
    "read_yaml",
    "resolve_path",
]


def read_yaml(
        config_path: str,
        validation_model: Optional[pydantic.main.ModelMetaclass] = None
):
    """Function to read STATIC config files."""

    config_path = Path(config_path).resolve(strict=True)

    with config_path.open() as config:
        loaded_file = yaml.load(config, Loader=yaml.FullLoader)

    if not loaded_file:
        loaded_file = dict()

    if validation_model:
        return validation_model(**loaded_file)

    return loaded_file


def resolve_path(root_dir: Optional[str], file_path: str) -> str:
    if root_dir is None or not root_dir.startswith('/'):
        root_dir = Path(file_path).resolve(strict=True).parent
    return root_dir
