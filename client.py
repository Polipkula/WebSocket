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

        # Wait for a response from the server
        response = await websocket.recv()
        print(f"Server response: {response}")

asyncio.run(connect())
