import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

async def send_messages(websocket):
     while True:
        message = await asyncio.to_thread(input, "> ")
        
        if message == "/quit":
            await websocket.close()
            break

        await websocket.send(message)
async def receive_messages(websocket):
    async for message in websocket:
        print(message)


async def main():
    username = input("Username: ")

    try:
        async with connect("ws://localhost:8765") as websocket:
            await websocket.send(username)
            send_task = asyncio.create_task(send_messages(websocket))
            receive_task = asyncio.create_task(receive_messages(websocket))

            done, pending = await asyncio.wait(
            [send_task, receive_task], 
            return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

            try:
                for task in pending:
                    task.cancel()
            except ConnectionClosed:
                print("\nConnection to server lost.")
    except OSError:
        print("Could not connect to server.\n" \
        "Make sure the server is running.")

if __name__ == "__main__":
    asyncio.run(main())