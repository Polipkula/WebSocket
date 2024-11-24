import asyncio
import websockets
import json

connected_clients = set()
document_content = ""
cursors = {}

async def handler(websocket, path):
    global document_content, cursors
    connected_clients.add(websocket)

    # Send the initial data to the client
    await websocket.send(json.dumps({
        "type": "init",
        "content": document_content,
        "cursors": cursors,
        "users": len(connected_clients),
    }))

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "update":
                document_content = data["content"]
                await broadcast({
                    "type": "update",
                    "content": document_content,
                })

            elif data["type"] == "cursor":
                cursors[websocket] = data["cursor"]
                await broadcast({
                    "type": "cursor",
                    "cursors": cursors,
                })

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)
        cursors.pop(websocket, None)
        await broadcast({
            "type": "disconnect",
            "users": len(connected_clients),
        })


async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])

async def main():
    async with websockets.serve(handler, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
