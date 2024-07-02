const express = require('express');
const mongoose = require('mongoose');

const app = express();
const port = process.env.PORT || 8085;

// MongoDB connection
const dbURL = process.env.MONGODB_URL || 'mongodb://localhost:27017/dbdata';
mongoose.connect(dbURL, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.log(err));

// Middleware
app.use(express.json());

// Simple route
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
