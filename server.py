import asyncio
import websockets
import json

connected_clients = set()
document_content = ""
cursors = {}

async def handler(websocket, path):
    global document_content, cursors
    connected_clients.add(websocket)

    # Send the current document content and list of connected users
    await websocket.send(json.dumps({
        "type": "init",
        "content": document_content,
        "cursors": cursors,
        "users": len(connected_clients)
    }))

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "update":
                # Update document content
                document_content = data["content"]
                # Broadcast to all clients
                await broadcast({
                    "type": "update",
                    "content": document_content
                })

            elif data["type"] == "cursor":
                # Update cursor position
                cursors[websocket] = data["cursor"]
                # Broadcast to all clients
                await broadcast({
                    "type": "cursor",
                    "cursors": cursors
                })

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        connected_clients.remove(websocket)
        cursors.pop(websocket, None)
        # Notify others about user disconnect
        await broadcast({
            "type": "disconnect",
            "users": len(connected_clients)
        })

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])

start_server = websockets.serve(handler, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
