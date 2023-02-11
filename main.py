from abc import ABC, abstractmethod
import asyncio
from datetime import datetime, timedelta
import logging
import sys
from typing import List

import aiohttp

from asyncduration import async_timed  # time duration decorator
from asynclogging import async_logging_to_file  # loging to file


logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")  # simple logging
URL_API_PRIVATBANK_ARCH = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
DAY_LIMIT = 10


class InterfaceOutput(ABC):
    @abstractmethod
    def show_out(self, *args, **kwargs):
        ...


class OutputAnswer(InterfaceOutput):
    """Show filtered result for certain currency."""

    @staticmethod
    def show_out(answers: List[dict], filter_currency: List[str]) -> str:
        """Give answer to the user."""
        if not answers or not filter_currency:
            answer = f'Something wrong on server?:\nstatus code {answers}\ncurrency request {filter_currency}'
            logging.critical(answer)
            return answer

        result = []
        for (
            record
        ) in (
            answers
        ):  # {"date":"01.12.2014",...,"exchangeRate":[{...,"currency":"CHF"...},...,{}]
            if not isinstance(record, dict):
                answer = f'Invalid server answer, status code:\n{answers}'
                logging.critical(answer)
                return answer

            key_day = record['date']
            result_day = {}
            for currency in filter_currency:  # 'EUR', 'USD', ...
                result_currency = {}
                for currency_in_record in record[
                    'exchangeRate'
                ]:  # [{...,"currency":"CHF"...},...,{}]
                    if currency_in_record['currency'] == currency:  # "currency":"CHF"
                        result_currency[currency] = {
                            'sale': currency_in_record.get('saleRate', None),
                            'purchase': currency_in_record.get('purchaseRate', None),
                        }  # result_currency = {'EUR': {...}}

                        result_day.update(result_currency)
            result.append({key_day: result_day})

        answer = f'Done:\n\t{result}'
        logging.info(answer)

        return answer


class ClientApplication:
    @async_timed()
    async def consumer(self, uri: str):
        """Get response from server."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(uri) as response:
                    if response.status == 200:  # all ok
                        # self.response_charset: str = response.headers['content-type'].split('charset=')[-1] if \
                        # 'charset=' in response.headers['content-type'] else None
                        # logging.info(f'CHARSET:\t{self.response_charset}')
                        # self.response_cookies = response.cookies
                        result = await response.json()  # get body of request
                        await async_logging_to_file(
                            f'\nInformation received: \t\t{datetime.now()}'
                        )
                        return result

                    else:
                        logging.error(f'Request error, status code:\n{response.status}')
                        return response.status

            except aiohttp.ClientConnectorError as err:  # others errors, restrictions by the provider, for example
                print(f'Connection error: {uri}', str(err))


class PrivatBankExchangeRate(ClientApplication):
    """Main class get the PrivatBank exchange rate."""

    def __init__(self, sys_argv: list) -> None:
        self.query_data = datetime.now().strftime('%d.%m.%Y')
        # logging.info(f'ToDay:\t{self.query_data}')
        try:
            # logging.info(f'Start with first parameter:\n{sys_argv[1]}')
            self.a_certain_past_day = (
                int(sys_argv[1]) if 0 < int(sys_argv[1]) < DAY_LIMIT else DAY_LIMIT
            )

        except (IndexError, TypeError):
            self.a_certain_past_day = 1

        self.uri = [
            f'''{URL_API_PRIVATBANK_ARCH}{(datetime.now()-timedelta(days=step)).strftime('%d.%m.%Y')}'''
            for step in range(self.a_certain_past_day)
        ]

        try:
            # logging.info(f'Other parameters:\n{sys_argv[2:]}')
            self.currency_list = sys_argv[2:] or ['EUR', 'USD']

        except IndexError:
            self.currency_list = ['EUR', 'USD']  # default

        print(
            f'{datetime.now()}\nReceive PrivatBank exchange rate for the last {self.a_certain_past_day} day(s)...\n'
        )

    async def get_exchange(self) -> tuple:
        """Create task list and return results."""
        tasks = [asyncio.create_task(self.consumer(uri)) for uri in self.uri]
        answer = await asyncio.gather(*tasks, return_exceptions=True) if tasks else None

        return answer, self.currency_list


@async_timed()
async def main(sys_argv: list) -> None:
    """Run application."""
    client = PrivatBankExchangeRate(sys_argv)
    server_answer, filter_currency = await client.get_exchange()
    
    return OutputAnswer.show_out(server_answer, filter_currency)


if __name__ == '__main__':
    logging.info(f'{datetime.now()}\nExample for run:\tpython main.py 5 USD EUR CHF\n')
    answer_for_request = asyncio.run(main(sys.argv))
