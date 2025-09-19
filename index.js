const express = require("express");
const app = express();
const path = require("path");

// app.get('/',(req,res)=>{
//     res.send("server is ready");
// })
app.use(express.static("public"));
app.get('/', (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
});

app.listen(3000, () => {
    console.log(`Server is running on localhost:3000`);
});