import asyncio
from websockets.asyncio.server import serve
from collections import deque
from datetime import datetime
import json
from websockets.exceptions import ConnectionClosed

connected_clients = {}
message_history = deque(maxlen=20)
HISTORY_FILE = "history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            for message in data:
                message_history.append(message)
    except FileNotFoundError:
        pass

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(list(message_history), file)


async def broadcast(message):
    for client in list(connected_clients):
        try:
            await client.send(message)
        except ConnectionClosed:
            connected_clients.pop(client, None)
        
async def send_message_history(websocket, show_empty=True):
    if not message_history:
        if show_empty:
            await websocket.send("No message history yet.")
        return
    await websocket.send("-- Recent Messages --")

    for old_message in message_history:
        await websocket.send(old_message)
    await websocket.send("-- End of Recent Messages --")

async def handle_client(websocket):
    username = (await websocket.recv()).strip()

    existing_usernames = [name.lower() for name in connected_clients.values()]

    if username == "":
        await websocket.send("Username cannot be empty.")
        await websocket.close()
        return

    if username.lower() in existing_usernames:
        await websocket.send("Username already taken.")
        await websocket.close()
        return

    connected_clients[websocket] = username

    print(f"{username} connected.")
    print(f"{len(connected_clients)} clients connected.")

    await send_message_history(websocket, show_empty=False)

    await broadcast(f"*** {username} joined the chat ***")

    try:
        async for message in websocket:

            handled, username = await handle_command(websocket, username, message)

            if handled:
                continue

            timestamp = datetime.now().strftime("%H:%M")

            formatted_message = f"[{timestamp}] {username}: {message}"

            message_history.append(formatted_message)
            save_history()

            print(formatted_message)
            await broadcast(formatted_message)

    finally:
        connected_clients.pop(websocket, None)

        await broadcast(
            f"*** {username} left the chat ***"
        )

        print(f"{username} disconnected.")
        print(f"{len(connected_clients)} clients connected.")

async def handle_command(websocket, username, message):

    if message == "/users":
        users = ", ".join(connected_clients.values())
        await websocket.send(f"Connected users: {users}")
        return True, username


    if message == "/help":
        await websocket.send(
            "Available commands:\n"
            "/help - Show available commands\n"
            "/users - List all connected users\n"
            "/quit - Disconnect from the server\n"
            "/rename_to <new_username> - Change your username\n"
            "/history - Show recent public messages\n"
            "/msg <username> <message> - Send a private message"
        )
        return True, username


    if message == "/history":
        await send_message_history(websocket)
        return True, username


    if message == "/msg" or message.startswith("/msg "):
        parts = message.split(" ", 2)

        if len(parts) != 3:
            await websocket.send(
                "Usage: /msg <username> <message>"
            )
            return True, username

        target_username = parts[1]
        private_message = parts[2]

        target_found = False

        for client, name in connected_clients.items():
            if name.lower() == target_username.lower():
                await client.send(
                    f"[Private] {username}: {private_message}"
                )

                await websocket.send(
                    f"[Private to {name}] {private_message}"
                )

                target_found = True
                break

        if not target_found:
            await websocket.send("User not found.")

        return True, username


    if message == "/rename_to" or message.startswith("/rename_to "):
        parts = message.split(" ", 1)

        if len(parts) != 2:
            await websocket.send(
                "Usage: /rename_to <new_username>"
            )
            return True, username

        new_username = parts[1].strip()

        if new_username == "":
            await websocket.send(
                "Username cannot be empty."
            )
            return True, username

        if new_username.lower() == username.lower():
            await websocket.send(
                "This is already the currently set name for this user."
            )
            return True, username

        username_taken = False

        for client, name in connected_clients.items():
            if name.lower() == new_username.lower():
                username_taken = True
                break

        if username_taken:
            await websocket.send(
                "This username is taken."
            )
            return True, username

        old_username = username

        connected_clients[websocket] = new_username
        username = new_username

        await broadcast(
            f"*** {old_username} changed their username "
            f"to {new_username} ***")
        return True, username

    if message.startswith("/"):
        await websocket.send("Unknown command. Type /help to see available commands.")
        return True, username
    return False, username

async def shutdown():
    for client in list(connected_clients):
        await client.close()

async def main():
    load_history()

    try:
        async with serve(handle_client, "localhost", 8765):
            print("Server started on localhost:8765")
            await asyncio.Future()

    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")