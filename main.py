import asyncio
import logging
from timeit import default_timer


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')


def duration(fun):
    def inner(*args, **kwargs):
        start: float = default_timer()
        rez = fun()
        logging.info(f'{default_timer()-start=} sec')

        return rez

    return inner


async def download_it():
    print('Download function...')
    await asyncio.sleep(1)
    print('After sleep')
    return 'downloaded data'

# @duration
async def main():
    # print(default_timer())
    print('Main function...')
    response = download_it()
    result = await response
    print(f'{result=}')


if __name__ == "__main__":
    asyncio.run(main())





