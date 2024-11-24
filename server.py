import asyncio
import websockets
import json

connected_clients = set()
document_content = ""
cursors = {}

# Handler pro WebSocket připojení
async def handler(websocket, path):  # Argument 'path' musí být přítomen
    global document_content, cursors
    connected_clients.add(websocket)

    # Odeslat inicializační zprávu
    await websocket.send(json.dumps({
        "type": "init",
        "content": document_content,
        "cursors": {id(client): cursor for client, cursor in cursors.items()},
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
                    "cursors": {id(client): cursor for client, cursor in cursors.items()},
                })

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)
        if websocket in cursors:
            del cursors[websocket]
        await broadcast({
            "type": "disconnect",
            "users": len(connected_clients),
        })


# Vysílání zpráv všem klientům
async def broadcast(message):
    if connected_clients:
        await asyncio.gather(*[client.send(json.dumps(message)) for client in connected_clients])

# Hlavní funkce serveru
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8080):  # Naslouchání na všech IP adresách
        print("WebSocket server running on ws://0.0.0.0:8080")
        await asyncio.Future()  # Nekonečný běh

if __name__ == "__main__":
    asyncio.run(main())
