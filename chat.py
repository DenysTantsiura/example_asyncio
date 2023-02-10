import asyncio
from datetime import datetime
import logging
import websockets
import names  # генеруватиме випадкове ім'я користувачеві
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from main import main as PBexchange

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith('exchange'):
                await self.send_to_clients(f'{ws.name}: {message} start '
                                           f'on {datetime.now()}\n(Example for run:\texchange 5 USD EUR CHF)\n')
                message = await self.get_exchange_currency(message)
                await self.send_to_clients(f"Server: {message}")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")

    @staticmethod
    async def get_exchange_currency(message: str) -> str:
        return await PBexchange(message.split(' '))


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
