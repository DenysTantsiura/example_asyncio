from abc import ABC, abstractmethod
import asyncio
from datetime import datetime, timedelta
import logging
import sys
from timeit import default_timer
from typing import Any

# from aiofile import async_open
import aiohttp
# import requests

from asyncduration import async_timed
from asynclogging import async_logging_to_file


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
URL_API_PRIVATBANK_ARCHIVE = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
DAY_LIMIT = 10


class InterfaceOutput(ABC):

    @abstractmethod
    def show_out(self, *args, **kwargs):
        ...    


class OutputAnswer(InterfaceOutput):

    @staticmethod
    def show_out(answer: list, filter_currency: list) -> bool:
        """Show answer for the user."""
        if not answer or not filter_currency:
            logging.info(f'Q!:\n{answer}\n{filter_currency}')
            return False
        
        result = []
        for exchange_on_day in answer:  # {"date":"01.12.2014",...,"exchangeRate":[{...,"currency":"CHF"...},...,{}]
            key_1 = exchange_on_day['date']
            result_day = {}
            for currency in filter_currency:  # 'EUR', 'USD', ...
                result_currency = {}
                for currency_in_list in exchange_on_day['exchangeRate']:  # [{...,"currency":"CHF"...},...,{}]
                    if currency_in_list['currency'] == currency:  # "currency":"CHF"
                        result_currency[currency] = {
                                                'sale': currency_in_list.get('saleRate', None), 
                                                'purchase': currency_in_list.get('purchaseRate', None)
                                                }  # result_currency = {'EUR': {...}}
                        
                        result_day.update(result_currency)
            result.append({key_1: result_day})

        logging.info(f'Done:\n{result}')

        return True
    
    
class ClientApplication:
    @async_timed()
    async def consumer(self, uri: str):  # hostname: str, port: int):
    
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                if response.status == 200:  # or '200'?
                    self.response_charset: str = response.headers['content-type'].split('charset=')[-1] if 'charset=' in response.headers['content-type'] else None
                    logging.info(f'CHARSET:\t{self.response_charset}')
                    # print("Content-type:", response.headers['content-type'])
                    # print('Cookies: ', response.cookies)
                    self.response_cookies = response.cookies
                    result = await response.json()
                    await async_logging_to_file(f'{result}\nreceived: \t\t{datetime.now()}')
                    return result
                else:
                    return response.status
    
    
class PrivatBankExchangeRate(ClientApplication):
    """Main class get the PrivatBank exchange rate."""
    
    def __init__(self) -> None:

        self.query_data = datetime.now().strftime('%d.%m.%Y')  # check! %m
        logging.info(f'Now:\t{self.query_data}')
        try:
            logging.info(f'Start with first parameter:\n{sys.argv[1]}')
            self.a_certain_past_day = int(sys.argv[1]) if int(sys.argv[1]) <= DAY_LIMIT else DAY_LIMIT # check to int?

        except (IndexError, TypeError):
            self.a_certain_past_day = 1  # int?
        
        self.uri = [f'''{URL_API_PRIVATBANK_ARCHIVE}{(datetime.now()-timedelta(days=step)).strftime('%d.%m.%Y')}''' for step in range(self.a_certain_past_day)]
        
        try:
            logging.info(f'Other parameters:\n{sys.argv[2:]}')
            self.currency_list = sys.argv[2:] or ['EUR', 'USD']

        except IndexError:
            self.currency_list = ['EUR', 'USD']

        print(f'{datetime.now()}\nPrivatBank exchange rate for the last {self.a_certain_past_day} day(s):\n')

    async def get_exchange(self) -> tuple:
        
        tasks = [asyncio.create_task(self.consumer(uri)) for uri in self.uri]
        # logging.info(f'Tasks:\n{tasks}')
        answer = await asyncio.gather(*tasks, return_exceptions=True) if tasks else None
        # logging.info(f'Answer:\n{answer}')

        return answer, self.currency_list
  

@async_timed()
async def main():

    client = PrivatBankExchangeRate()
    server_answer, filter_currency = await client.get_exchange()
    OutputAnswer.show_out(server_answer, filter_currency)
    

if __name__ == "__main__":
    asyncio.run(main())

# poetry remove httpx
# poetry remove requests
