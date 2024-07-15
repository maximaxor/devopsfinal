const express = require('express');
const mongoose = require('mongoose');

const app = express();
const port = process.env.PORT || 8085;

// MongoDB connection
const dbURL = process.env.MONGODB_URL || 'mongodb://mongodb:27017';
mongoose.connect(dbURL, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.log('MongoDB connection error:', err));

// Middleware
app.use(express.json());

// Simple route
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// Schema for License Plates
const licensePlateSchema = new mongoose.Schema({
    license_plate: String,
    owner: String,
    model: String,
    color: String,
    engine_model: String,
    manufacturing_date: String,
    car_type: String,
    fanciness: String,
});

const LicensePlate = mongoose.model('LicensePlate', licensePlateSchema);

// Endpoint to store license plate data
app.post('/store_license_plate', async (req, res) => {
    try {
        console.log('Received request:', req.body);  // Log the incoming request
        const licensePlateData = req.body;
        const licensePlate = new LicensePlate(licensePlateData);
        await licensePlate.save();
        res.status(200).json({ message: 'Data stored successfully' });
    } catch (error) {
        console.error('Error storing data:', error);  // Log the error
        res.status(500).json({ error: 'Failed to store data' });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
