import logging
# from time import time
from timeit import default_timer


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')


def duration(fun):
    def inner(*args, **kwargs):
        start: float = default_timer()
        rez = fun()
        logging.info(f'{default_timer()-start=} sec')

        return rez

    return inner


@duration
def main():
    print(default_timer())


if __name__ == "__main__":
    main()





