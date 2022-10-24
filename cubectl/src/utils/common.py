import yaml
from pathlib import Path
from functools import cache
import pydantic
from typing import Optional, Union


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


def resolve_path(root_dir: Optional[Union[Path, str]], file_path: str, return_dir: bool = False) -> str:
    # resolved_path = str(root_dir)

    if str(file_path).startswith('/'):
        resolved_path = Path(file_path)
    elif file_path is None:
        resolved_path = Path(root_dir)
    elif root_dir is None or not str(root_dir).startswith('/'):
        resolved_path = Path(file_path).resolve(strict=True)
    else:
        resolved_path = Path(root_dir, file_path)

    if return_dir:
        if resolved_path.is_file():
            resolved_path = resolved_path.parent
        elif resolved_path.is_dir():
            pass
    return str(resolved_path)
