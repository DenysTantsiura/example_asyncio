import logging
import pathlib


key_file = 'key.txt'

logging.basicConfig(level=logging.CRITICAL, format='%(message)s')


def watcher(function):
    def inner_eye(*args, **kwargs):
        try:
            rez = function(*args, **kwargs)

        except Exception as error:
            logging.critical(f'Something wrong!, system error:\n{error}')
            rez = f'{error}'    

        return rez
    
    return inner_eye


@watcher
def save_key(key: str) -> None:
    with open(key_file, "w") as fh:
        fh.write(key)


@watcher
def load_key() -> str:
    with open(key_file, "r") as fh:
        return fh.readline()


def get_api_key() -> str:
    """Return api-key from local file or user input in CLI."""
    if pathlib.Path(key_file).exists():
        print('Ok! Key-file found.')
        key = load_key()

    else:
        key: str = input('Enter the KEY:\n')
        save_key(key) if key else None
    
    return key
