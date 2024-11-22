const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    // loginToken: { type: String, default: '' },
    // tokenExpire: { type: Number, default: -1 },
    sensitivity: { type: Number, default: 0 },
});

module.exports = mongoose.model('User', UserSchema);
