import asyncio
import sys
import server
import client

def main():
    if len(sys.argv) != 2:
        print("Please enter a valid command.")
    else:
        command = sys.argv[1].lower()
        if command == "start":
            try:
                asyncio.run(server.main())
            except KeyboardInterrupt:
                print("\nServer stopped.")
        elif command == 'connect':
            asyncio.run(client.main())
        elif command == 'help':
            print("List of commands:\nstart: starts the server. \nconnect: connects the client to the server.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()