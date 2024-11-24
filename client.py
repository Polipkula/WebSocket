import asyncio
import websockets
import json

# Připojení ke WebSocket serveru
async def connect():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected to the server!")

        # Poslání testovací zprávy
        await websocket.send(json.dumps({
            "type": "update",
            "content": "Hello, WebSocket!",
        }))

        # Čekání na odpovědi od serveru
        try:
            while True:
                response = await websocket.recv()
                print(f"Server response: {response}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")

# Spuštění klienta
asyncio.run(connect())
