import asyncio
from websockets.asyncio.client import connect

async def send_messages(websocket):
     while True:
        message = await asyncio.to_thread(input, "> ")
        await websocket.send(message)
        if message == "/quit":
            await websocket.close()
async def receive_messages(websocket):
    async for message in websocket:
        print(message)


async def main():
    async with connect("ws://localhost:8765") as websocket:
        print("Sucessfully connected to server.")
        await asyncio.gather(send_messages(websocket), 
                             receive_messages(websocket))

if __name__ == "__main__":
    asyncio.run(main())