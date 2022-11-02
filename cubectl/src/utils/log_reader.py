import os

from pathlib import Path
from logging import getLogger
from time import sleep
from typing import Protocol


__all__ = [
    "LogReaderProtocol",
    "LogReader",
]

log = getLogger(__file__)


class LogReaderProtocol(Protocol):
    def get_log(self, head: int = None, tail: int = None):
        ...

    def get_latest_log(self, head: int = None, tail: int = None):
        ...


class LogReader:
    def __init__(self, log_file: str):
        self._raw_log_file = log_file
        if not log_file or not Path(log_file).is_file():
            log.warning(
                f'cubectl: service_process: LogReader: log file {log_file}, not found.'
            )
            self._log = None
        else:
            self._log = Path(log_file)
        self._seek_cursor = None
        self._file_stat = None

    def get_log(self, head: int = None, tail: int = None):
        if not self._log:
            return f"No logfile found for {self._raw_log_file}."

        self._update_file_info()

        with self._log.open() as f:
            try:
                result = get_file_lines(fd=f, head=head, tail=tail)
                self._seek_cursor = f.tell()
            except UnicodeDecodeError as ude:
                log.warning(f'cubectl: log_reader: logfile: {self._log} raised {ude} during reading.')
                self._seek_cursor = 0

        self._update_file_info()
        return "".join(result)

    def get_latest_log(self, head: int = None, tail: int = None):
        result = []

        if not self._log:
            return f"No logfile found for {self._raw_log_file}."

        if _is_new_file(new_stat=self._log.stat(), old_stat=self._file_stat):
            return self.get_log(head=head, tail=tail)

        if _is_file_changed(new_stat=self._log.stat(), old_stat=self._file_stat):
            with self._log.open() as f:
                self._update_file_info()
                try:
                    result = get_file_lines(fd=f, head=head, tail=tail, seek_cursor=self._seek_cursor)
                    self._seek_cursor = f.tell()
                except UnicodeDecodeError as ude:
                    log.warning(f'cubectl: log_reader: logfile: {self._log} raised {ude} during reading.')
                    self._seek_cursor = 0

        self._update_file_info()
        return "".join(result)

    def _update_file_info(self):
        s = self._log.stat()
        if self._file_stat is None:
            self._seek_cursor = 0
        elif s.st_size < self._file_stat.st_size:
            self._seek_cursor = s.st_size
        self._file_stat = s


def truncate_list(list_object: list, head=None, tail=None):
    result = list_object.copy()
    if head:
        result = result[:head]
    if tail:
        result = result[-tail:]
    return result


def get_file_lines(fd, head: int = None, tail: int = None, seek_cursor: int = 0):
    result = []
    fd.seek(seek_cursor)

    if head:
        for _ in range(head):
            result.append(fd.readline())
    else:
        for line in fd.readlines():
            result.append(line)

    return truncate_list(result, tail=tail)


def _is_file_changed(new_stat: os.stat_result, old_stat: os.stat_result = None) -> bool:
    is_changed = False

    if old_stat is None:
        is_changed = True

    if new_stat.st_mtime != old_stat.st_mtime:
        is_changed = True

    return is_changed


def _is_new_file(new_stat: os.stat_result, old_stat: os.stat_result = None) -> bool:
    if old_stat is not None:
        return new_stat.st_ctime < old_stat.st_ctime
    return True


def main():
    log_file_str = 'input.txt'
    log_file = Path(log_file_str)
    lr = LogReader(log_file=log_file_str)

    while True:
        result = lr.get_latest_log()
        if result.strip():
            print(result)
            print('-')
        sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
