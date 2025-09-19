const express = require("express");
const app = express();
const path = require("path");
const axios = require('axios');

// app.get('/',(req,res)=>{
//     res.send("server is ready");
// })

app.use(express.json());
app.use(express.static("public"));

// Forward chat requests to Python Flask server
app.post('/chat', async (req, res) => {
    try {
        // Send message to Python server
        const response = await axios.post('http://localhost:5000/chat', {
            message: req.body.message
        });
        
        // Send back Python server's response
        res.json(response.data);
    } catch (error) {
        res.json({ reply: "Sorry, Python server is not running!" });
    }
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
});

app.listen(3000, () => {
    console.log(`Server is running on localhost:3000`);
    console.log(' Python Flask server is running on port 5000');
});