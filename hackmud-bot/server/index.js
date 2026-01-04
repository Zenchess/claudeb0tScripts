const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

const PORT = 3000;

// Paths
const BOT_DIR = path.join(__dirname, '..', 'bot');
const MEMORY_FILE = path.join(BOT_DIR, 'memory.json');
const STATE_FILE = path.join(BOT_DIR, 'state.json');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'web')));

// Store for logs and chat history
let logs = [];
let chatHistory = [];
let currentState = { status: 'offline' };
let currentMemory = {};

// API Routes
app.get('/api/status', (req, res) => {
    res.json({
        state: currentState,
        memory: currentMemory,
        logs: logs.slice(-100),
        chat: chatHistory.slice(-50)
    });
});

app.get('/api/memory', (req, res) => {
    try {
        if (fs.existsSync(MEMORY_FILE)) {
            const memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
            res.json(memory);
        } else {
            res.json({});
        }
    } catch (e) {
        res.json({ error: e.message });
    }
});

app.post('/api/memory', (req, res) => {
    try {
        fs.writeFileSync(MEMORY_FILE, JSON.stringify(req.body, null, 2));
        res.json({ success: true });
    } catch (e) {
        res.json({ error: e.message });
    }
});

app.get('/api/state', (req, res) => {
    try {
        if (fs.existsSync(STATE_FILE)) {
            const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
            res.json(state);
        } else {
            res.json({});
        }
    } catch (e) {
        res.json({ error: e.message });
    }
});

// Socket.IO connections
io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    // Send current state to new client
    socket.emit('init', {
        state: currentState,
        memory: currentMemory,
        logs: logs.slice(-100),
        chat: chatHistory.slice(-50)
    });

    // User sends a message to the bot
    socket.on('user_message', (data) => {
        console.log('User message:', data.message);
        const chatEntry = {
            sender: 'user',
            message: data.message,
            time: new Date().toLocaleTimeString()
        };
        chatHistory.push(chatEntry);

        // Broadcast to all clients (including web dashboard)
        io.emit('chat_message', chatEntry);

        // The bot agent will pick this up via its socket connection
    });

    // Control commands from web interface
    socket.on('command', (data) => {
        console.log('Command:', data.command);
        // Forward to all connections (bot will receive this)
        io.emit('command', data);
    });

    // Bot sends a log entry
    socket.on('bot_log', (data) => {
        logs.push(data);
        if (logs.length > 1000) logs = logs.slice(-500);
        io.emit('bot_log', data);
    });

    // Bot sends state update
    socket.on('bot_state', (data) => {
        currentState = data.state || currentState;
        currentMemory = data.memory || currentMemory;
        io.emit('bot_state', data);
    });

    // Bot sends chat message
    socket.on('chat_message', (data) => {
        chatHistory.push(data);
        if (chatHistory.length > 200) chatHistory = chatHistory.slice(-100);
        io.emit('chat_message', data);
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
    });
});

// Start server
server.listen(PORT, () => {
    console.log(`Hackmud Bot Server running at http://localhost:${PORT}`);
    console.log(`Open your browser to http://localhost:${PORT}`);
});
