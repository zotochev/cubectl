import os
from time import sleep

import click


@click.command()
@click.option('--name', default='foobar', help='Number of greetings.')
def main(name):
    while True:
        # print(f'{os.getpid()}: {name=}')
        sleep(2)


if __name__ == "__main__":
    main()
