import asyncio
import websockets

async def connect():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected to the server!")
        await websocket.send("Hello Server!")
        response = await websocket.recv()
        print(f"Server says: {response}")

asyncio.run(connect())
