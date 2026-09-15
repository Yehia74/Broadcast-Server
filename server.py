import asyncio
from websockets.asyncio.server import serve

connected_clients = set()

async def handle_client(websocket):
    connected_clients.add(websocket)
    print(f"{len(connected_clients)} clients connected.")
    try:
        async for message in websocket:
            print(message)
            for client in connected_clients:
                await client.send(message)
    finally:
        connected_clients.remove(websocket)
        print(f"{len(connected_clients)} clients connected.")


async def main():
    async with serve(handle_client, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())