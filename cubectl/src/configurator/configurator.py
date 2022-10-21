class Configurator:
    """
    Opens status file and sets it in requested state.
    """

    def __init__(self, services: list, status_file: str):
        self._services = services
        self._status_file = self._read_file(status_file)

    @staticmethod
    def _read_file(status_file: str):
        """
        Reads status file (yaml) to dict
        :param status_file:
        :return:
        """

        return dict()

    def start(self):
        """
        1. status file does not have service set up in init
        2. status file has service set up in init
        3. status of service does not conflict with command
        4. status of service conflicts with command
        """
        pass
