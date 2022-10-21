import os
from time import sleep
import dotenv

import click


@click.command()
@click.option('--name', default='foobar', help='Number of greetings.')
def main(name):
    # dotenv.load_dotenv()
    while True:
        print(
            f'{os.getpid()}: {name=}, '
            f'ENV:: '
            f'ONE={os.environ.get("ONE")}; '
            f'TWO={os.environ.get("TWO")}; '
            f'THREE={os.environ.get("THREE")}'
        )
        sleep(2)


if __name__ == "__main__":
    main()
