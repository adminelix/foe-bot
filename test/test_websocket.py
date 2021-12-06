import asyncio

import websockets


async def printer(websocket):
    async for message in websocket:
        print(message)


async def main():
    async with websockets.serve(printer, "wss://de14.forgeofempires.com/socket/"):
        await asyncio.Future()  # run forever


def test_main():
    main()
