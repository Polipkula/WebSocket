const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path'); // Pro manipulaci s cestami

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Statické soubory
app.use(express.static(path.join(__dirname)));

// Výchozí cesta
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html')); // Odpověď na GET /
});

// Data
let documentText = ""; // Text dokumentu
let users = []; // Seznam uživatelů

// WebSocket logika
wss.on('connection', (ws) => {
    const userId = `User-${Math.random().toString(36).substr(2, 9)}`;
    const userColor = `hsl(${Math.floor(Math.random() * 360)}, 70%, 70%)`; // Unikátní barva
    users.push({ userId, userColor });

    ws.send(JSON.stringify({ type: 'init', text: documentText, users }));

    wss.clients.forEach((client) => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ type: 'user_connected', userId, userColor }));
        }
    });

    ws.on('message', (message) => {
        const data = JSON.parse(message);

        if (data.type === 'update_text') {
            documentText = data.text; // Aktualizace textu na serveru
            wss.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({ type: 'update_text', text: documentText, userId }));
                }
            });
        }

        if (data.type === 'cursor_position') {
            wss.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN && client !== ws) {
                    client.send(JSON.stringify({
                        type: 'cursor_position',
                        userId,
                        position: data.position,
                        userColor,
                    }));
                }
            });
        }

        if (data.type === 'selection') {
            // Přeposlat označení všem ostatním klientům
            wss.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN && client !== ws) {
                    client.send(JSON.stringify({
                        type: 'selection',
                        userId,
                        selection: data.selection,
                        userColor,
                    }));
                }
            });
        }
    });

    ws.on('close', () => {
        users = users.filter((user) => user.userId !== userId);
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({ type: 'user_disconnected', userId }));
            }
        });
    });
});

// Spuštění serveru
server.listen(8080, () => {
    console.log('Server is running on http://localhost:8080');
});
