import asyncio
import httpx
import logging
from timeit import default_timer

from authentication import get_api_key  # www.pexels.com/uk-ua/api/


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

URL = 'https://api.pexels.com/v1/search'
API_KEY = get_api_key()

def duration(fun):
    def inner(*args, **kwargs):
        start: float = default_timer()
        rez = fun()
        logging.info(f'{default_timer()-start=} sec')

        return rez

    return inner


async def download_it(query: str, current_count: int) -> None:
    headers = {'Authorization': API_KEY}
    params = {
        'query': query,
        'per_page': 1,
        'page': current_count,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(URL, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for item in data['photos']:
                print(item['src']['original'])
        else:
            print(f'{response.status_code=}, {response.json()=}')
    print(f'{query} - - - - - - - {current_count}')

    # print('Download function...')
    # await asyncio.sleep(1)
    # print('After sleep')
    # return 'downloaded data'


@duration
async def main():
    query = 'car'
    page_count = 5
    current_count: int = 0
    while current_count < page_count:
        current_count += 1
        await download_it(query, current_count)
    # # print(default_timer())
    # print('Main function...')
    # response = download_it()
    # result = await response
    # print(f'{result=}')


if __name__ == "__main__":
    asyncio.run(main())


# poetry add httpx



