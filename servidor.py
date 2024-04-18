import asyncio
import random

class ObjectServer:
    def __init__(self):
        self.clients = set()

    async def handle_client(self, reader, writer):
        self.clients.add(writer)
        try:
            while True:
                x_coord = random.randint(0, 800)
                await self.send_object(writer, x_coord)
                await asyncio.sleep(1)
        finally:
            self.clients.remove(writer)

    async def send_object(self, writer, x_coord):
        message = str(x_coord).encode()
        writer.write(message)
        await writer.drain()

async def main():
    server = ObjectServer()
    server_runner = await asyncio.start_server(server.handle_client, '127.0.0.1', 8888)

    async with server_runner:
        await server_runner.serve_forever()

asyncio.run(main())