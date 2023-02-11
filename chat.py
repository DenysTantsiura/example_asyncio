import asyncio
from datetime import datetime
import logging
import websockets
import names  # генеруватиме випадкове ім'я користувачеві
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from main import main as PBexchange

logging.basicConfig(level=logging.INFO)  # simple logging


class Server:
    clients = set()  # remember clients

    async def register(self, ws: WebSocketServerProtocol):
        """Register a new client."""
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        """Unregister client."""
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        """Send a message to each client."""
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        """Handler, registration websocket connection, distrubute..."""
        await self.register(ws)  # when the client has connected - register it
        try:
            await self.distrubute(ws)

        except ConnectionClosedOK:
            pass

        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        """distrubute for ecah websocket."""
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
        """Additional function: get the exchange rate from PrivatBank."""
        return await PBexchange(message.split(' '))


async def main():
    server = Server()  # create a server instance
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())  # entry point
