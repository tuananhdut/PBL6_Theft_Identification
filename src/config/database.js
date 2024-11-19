const mongoose = require('mongoose');
require('dotenv').config()

// MongoDB connection string
const MONGOURI = process.env.MONGOURI

// Connect to MongoDB
const connectDB = async () => {
    try {
        await mongoose.connect(MONGOURI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
        console.log('MongoDB connected...');
    } catch (err) {
        console.error('Database connection error:', err.message);
        process.exit(1); // Exit process with failure
    }
};

module.exports = connectDB;
