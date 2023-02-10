from abc import ABC, abstractmethod
import asyncio
from datetime import datetime, timedelta
import logging
import sys
from typing import List

import aiohttp

from asyncduration import async_timed
from asynclogging import async_logging_to_file


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
URL_API_PRIVATBANK_ARCH = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
DAY_LIMIT = 10


class InterfaceOutput(ABC):

    @abstractmethod
    def show_out(self, *args, **kwargs):
        ...    


class OutputAnswer(InterfaceOutput):
    """Show filtered result for certain currency."""
    @staticmethod
    def show_out(answers: List[dict], filter_currency: List[str]) -> bool:
        """Show answer for the user."""
        if not answers or not filter_currency:
            logging.critical(f'Something wrong on server?:\nstatus code {answers}\ncurrency request {filter_currency}')
            return False
        
        result = []
        for record in answers:  # {"date":"01.12.2014",...,"exchangeRate":[{...,"currency":"CHF"...},...,{}]
            if not isinstance(record, dict):
                logging.critical(f'Invalid server answer, status code:\n{answers}')
                return False
            
            key_day = record['date']
            result_day = {}
            for currency in filter_currency:  # 'EUR', 'USD', ...
                result_currency = {}
                for currency_in_record in record['exchangeRate']:  # [{...,"currency":"CHF"...},...,{}]
                    if currency_in_record['currency'] == currency:  # "currency":"CHF"
                        result_currency[currency] = {
                                                'sale': currency_in_record.get('saleRate', None), 
                                                'purchase': currency_in_record.get('purchaseRate', None)
                                                }  # result_currency = {'EUR': {...}}
                        
                        result_day.update(result_currency)
            result.append({key_day: result_day})

        logging.info(f'Done:\n\t{result}')

        return True
    
    
class ClientApplication:
    @async_timed()
    async def consumer(self, uri: str):
        """Get response from server."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(uri) as response:
                    if response.status == 200:  # or '200'?
                        # self.response_charset: str = response.headers['content-type'].split('charset=')[-1] if \
                        # 'charset=' in response.headers['content-type'] else None
                        # logging.info(f'CHARSET:\t{self.response_charset}')
                        # self.response_cookies = response.cookies
                        result = await response.json()
                        await async_logging_to_file(f'\n{result}\nreceived: \t\t{datetime.now()}')
                        return result
                    
                    else:
                        logging.error(f'Request error, status code:\n{response.status}')
                        return response.status
                    
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {uri}', str(err))
    
    
class PrivatBankExchangeRate(ClientApplication):
    """Main class get the PrivatBank exchange rate."""
    def __init__(self) -> None:

        self.query_data = datetime.now().strftime('%d.%m.%Y')
        # logging.info(f'ToDay:\t{self.query_data}')
        try:
            # logging.info(f'Start with first parameter:\n{sys.argv[1]}')
            self.a_certain_past_day = int(sys.argv[1]) if 0 < int(sys.argv[1]) < DAY_LIMIT else DAY_LIMIT

        except (IndexError, TypeError):
            self.a_certain_past_day = 1
        
        # self.uri = [f'''{URL_API_PRIVATBANK_ARCH}{(datetime.now()-timedelta(days=step)).strftime('%d.%m.%Y')}'''\
        #  for step in range(self.a_certain_past_day)]
        self.uri = []
        for day in range(self.a_certain_past_day):
            query: datetime = datetime.now()-timedelta(days=day)
            self.uri.append(f'''{URL_API_PRIVATBANK_ARCH}{query.strftime('%d.%m.%Y')}''')
        
        try:
            # logging.info(f'Other parameters:\n{sys.argv[2:]}')
            self.currency_list = sys.argv[2:] or ['EUR', 'USD']

        except IndexError:
            self.currency_list = ['EUR', 'USD']

        print(f'{datetime.now()}\nReceive PrivatBank exchange rate for the last {self.a_certain_past_day} day(s)...\n')

    async def get_exchange(self) -> tuple:
        
        tasks = [asyncio.create_task(self.consumer(uri)) for uri in self.uri]
        answer = await asyncio.gather(*tasks, return_exceptions=True) if tasks else None

        return answer, self.currency_list
  

@async_timed()
async def main() -> None:
    """Run application."""
    client = PrivatBankExchangeRate()
    server_answer, filter_currency = await client.get_exchange()
    OutputAnswer.show_out(server_answer, filter_currency)
    

if __name__ == "__main__":
    print(f'{datetime.now()}\nExample for run:\tpython main.py 5 USD EUR CHF\n')
    asyncio.run(main())
