// const express = require("express");
// const app = express();
// const path = require("path");
// const axios = require('axios');

// // app.get('/',(req,res)=>{
// //     res.send("server is ready");
// // })

// app.use(express.json());
// app.use(express.static("public"));

// // Forward chat requests to Python Flask server
// app.post('/chat', async (req, res) => {
//     try {
//         // Send message to Python server
//         const response = await axios.post('http://localhost:5000/chat', {
//             message: req.body.message
//         });
        
//         // Send back Python server's response
//         res.json(response.data);
//     } catch (error) {
//         res.json({ reply: "Sorry, Python server is not running!" });
//     }
// });

// app.get('/', (req, res) => {
//     res.sendFile(__dirname + "/public/index.html");
// });

// app.listen(3000, () => {
//     console.log(`Server is running on localhost:3000`);
//     console.log(' Python Flask server is running on port 5000');
// });

const express = require("express");
const app = express();
const path = require("path");
const axios = require('axios');
const { spawn } = require('child_process');

// Configuration
const EXPRESS_PORT = 3000;
const PYTHON_PORT = 5000;
const PYTHON_START_DELAY = 3000; // 3 seconds to let Python server start

let pythonProcess = null;
let pythonServerReady = false;

// Start Python Flask server automatically
function startPythonServer() {
    console.log(' Starting Python Flask server ');
    
    pythonProcess = spawn('python', ['app.py'], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PORT: '5000' }
    });

    pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(` Python: ${output}`);
        
        // Check if Flask server is ready
        if (output.includes('Running on') || output.includes('* Debug mode:')) {
            pythonServerReady = true;
            console.log(' Python Flask server is ready!');
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(` Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(` Python process exited with code ${code}`);
        pythonServerReady = false;
    });

    pythonProcess.on('error', (error) => {
        console.error(` Failed to start Python process: ${error}`);
        pythonServerReady = false;
    });

    // Give Python server time to start
    setTimeout(() => {
        if (!pythonServerReady) {
            console.log(' Python server taking longer to start...');
        }
    }, PYTHON_START_DELAY);
}

// Health check for Python server
async function checkPythonServer() {
    try {
        await axios.get(`http://localhost:${PYTHON_PORT}/`);
        return true;
    } catch (error) {
        return false;
    }
}

// Middleware
app.use(express.json());
app.use(express.static("public"));

// Main route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Health check endpoint
app.get('/api/health', async (req, res) => {
    const pythonHealthy = await checkPythonServer();
    res.json({
        express: 'healthy',
        python: pythonHealthy ? 'healthy' : 'unavailable',
        timestamp: new Date().toISOString()
    });
});

// Chat endpoint with better error handling
app.post('/api/chat', async (req, res) => {
    try {
        if (!req.body.message) {
            return res.status(400).json({ 
                reply: "Please provide a message",
                error: "Missing message in request body"
            });
        }

        // Check if Python server is ready
        if (!pythonServerReady) {
            const isReady = await checkPythonServer();
            if (!isReady) {
                return res.json({ 
                    reply: "Chatbot is starting up, please try again in a moment...",
                    status: "python_server_unavailable"
                });
            }
            pythonServerReady = true;
        }

        console.log(' Forwarding message to Python server:', req.body.message);
        
        // Send message to Python server
        const response = await axios.post(`http://localhost:${PYTHON_PORT}/chat`, {
            message: req.body.message
        }, {
            timeout: 10000 // 10 second timeout
        });
        
        console.log('Received response from Python server');
        
        // Send back Python server's response
        res.json(response.data);
        
    } catch (error) {
        console.error(' Error communicating with Python server:', error.message);
        
        if (error.code === 'ECONNREFUSED') {
            res.json({ 
                reply: "Chatbot service is temporarily unavailable. Please try again in a moment.",
                error: "python_server_connection_refused"
            });
        } else if (error.code === 'TIMEOUT') {
            res.json({ 
                reply: "The chatbot is taking too long to respond. Please try again.",
                error: "python_server_timeout"
            });
        } else {
            res.json({ 
                reply: "Sorry, there was an error processing your message. Please try again.",
                error: "unknown_error"
            });
        }
    }
});

// Graceful shutdown
function gracefulShutdown() {
    console.log('\n Shutting down servers...');
    
    if (pythonProcess) {
        console.log(' Terminating Python process...');
        pythonProcess.kill('SIGTERM');
        
        // Force kill if it doesn't shut down gracefully
        setTimeout(() => {
            if (pythonProcess && !pythonProcess.killed) {
                console.log(' Force killing Python process...');
                pythonProcess.kill('SIGKILL');
            }
        }, 5000);
    }
    
    setTimeout(() => {
        console.log('Shutdown complete');
        process.exit(0);
    }, 1000);
}

// Handle shutdown signals
process.on('SIGINT', gracefulShutdown);
process.on('SIGTERM', gracefulShutdown);

// Start Python server first, then Express
startPythonServer();

// Start Express server
app.listen(EXPRESS_PORT, () => {
    console.log(`Express server running on http://localhost:${EXPRESS_PORT}`);
    console.log(` Python Flask server should be running on port ${PYTHON_PORT}`);
    console.log(' Chat requests will be forwarded to Python server');
    console.log('Health check available at /health');
    console.log( 'Use Ctrl+C to stop both servers');
});
