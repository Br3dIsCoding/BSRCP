const express = require('express');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');
const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// WebSocket server
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    console.log(`🟢 WebSocket client connected! Total clients: ${wss.clients.size}`);
});

function broadcastMeme(meme) {
    console.log(`📤 Broadcasting meme to ${wss.clients.size} clients:`, meme);
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(meme));
        }
    });
}

// Simple authentication
const VALID_TOKEN = 'your-secret-token-here';

// API endpoint for creating memes
app.post('/create-meme', (req, res) => {
    const { token, topText, bottomText, imageId } = req.body;
    
    if (token !== VALID_TOKEN) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    if (!imageId) {
        return res.status(400).json({ error: 'Image ID is required' });
    }
    
    const meme = {
        topText: topText || '',
        bottomText: bottomText || '',
        imageId: imageId,
        timestamp: Date.now()
    };
    
    // Also write to file
    const memeData = `${topText || ''}||${bottomText || ''}||${imageId}`;
    fs.writeFileSync(path.join(__dirname, 'meme.txt'), memeData);
    console.log('📝 Wrote meme to file:', memeData);
    
    broadcastMeme(meme);
    res.json({ success: true });
});

// Clear meme file endpoint
app.post('/clear-meme', (req, res) => {
    fs.writeFileSync(path.join(__dirname, 'meme.txt'), '');
    res.send('Cleared');
});

// POLLING METHOD - Check file every second
const memeFilePath = path.join(__dirname, 'meme.txt');
let lastMemeContent = '';

// Create file if it doesn't exist
if (!fs.existsSync(memeFilePath)) {
    fs.writeFileSync(memeFilePath, '');
    console.log('📄 Created meme.txt file');
}

console.log('👀 Starting file poller (checking every 1 second)');

setInterval(() => {
    try {
        // Read the file
        const content = fs.readFileSync(memeFilePath, 'utf8').trim();
        
        // If there's content and it's different from last time
        if (content && content !== lastMemeContent && content.includes('||')) {
            console.log('📁 New meme detected via polling:', content);
            lastMemeContent = content;
            console.log(lastMemeContent)
            const parts = content.split('||');
            if (parts.length >= 3) {
                const topText = parts[0];
                const bottomText = parts[1];
                const imageId = parts[2];
                
                console.log(`✅ Parsed meme - Top: ${topText}, Bottom: ${bottomText}, ID: ${imageId}`);
                
                broadcastMeme({
                    topText: topText,
                    bottomText: bottomText,
                    imageId: imageId,
                    timestamp: Date.now()
                });
                
                // Optional: Clear the file after broadcasting IMPORTANT SO THERE CAN BE DUPLICATES
                fs.writeFileSync(memeFilePath, '');
                lastMemeContent = '';
            }
        }
    } catch (err) {
        console.error('Error polling file:', err.message);
    }
}, 1000); // Check every 1000ms (1 second)

app.listen(PORT, () => {
    console.log(`✅ Server running on http://localhost:${PORT}`);
    console.log(`✅ WebSocket server on ws://localhost:8080`);
    console.log(`📁 Polling file: ${memeFilePath}`);
});