from pathlib import Path
from time import sleep
import os


def main():
    # file_path = Path('/home/mikhail/PycharmProjects/cubectl/cubectl/tests/assets/temp/enegan_status_file.yaml')
    #
    # while True:
    #     print(file_path.stat().st_mtime)
    #     sleep(1)
    print(os.geteuid())


if __name__ == "__main__":
    main()
