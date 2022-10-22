import logging
from pathlib import Path
import yaml


log = logging.getLogger(__file__)


class Executor:
    """
    Starts up processed
    Monitors processes state
    Applies changes from state file
    """

    def __init__(self, init_file):
        self._init_file = Path(init_file).resolve(strict=True)
        self._root_dir = self._resolve_root_dir(self._init_file)

    def start(self):
        _ = self

        while True:
            pass

    def update(self, status_file: dict):
        pass

    def _fix_all_paths_to_absolut(self, service_config):
        """
        fix in config:
            * file path
            * env files
        """
        pass

    @staticmethod
    def _resolve_root_dir(init_file):
        with init_file.open() as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            config_root_dir = config.get('root_dir')
            if config_root_dir is not None:
                if str(config_root_dir).startswith('/'):
                    return config_root_dir
            return init_file.parent
