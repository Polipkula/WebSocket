import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected to the server!")

        # Send an example update message
        await websocket.send(json.dumps({
            "type": "update",
            "content": "Hello, WebSocket!",
        }))

        # Wait for responses from the server
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Server response: {data}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by server")
                break

asyncio.run(connect())
