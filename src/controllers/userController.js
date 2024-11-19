const bcrypt = require('bcryptjs');
const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');



const createUser = async (req, res) => {

    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password are required.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = new User({
        username: username,
        password: hashedPassword
    })

    newUser.save()
        .then((User) => {
            res.status(200).json({ message: "User created successfully" });
        })
        .catch((err) => {
            if (err.code === 11000) {
                res.status(400).json({ error: "Username already exists" });
            } else {
                res.status(500).json({ error: "Server error" });
            }
        });
}

const login = async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json('Username and password are required.');
    }

    try {
        const user = await User.findOne({ username });

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }


        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }


        // Các phần của jwt
        // Header: alg, typ
        // payload: dữ liệu được mã hóa 
        // signature: chuỗi kí tự mã hóa
        const access_token = jwt.sign(
            { userId: user._id, username: user.username },
            process.env.JWT_SECRET,
            { expiresIn: '1h' }
        );

        user.loginToken = access_token;

        res.status(200).json({
            message: 'Login successful',
            access_token
        });
    } catch (err) {
        res.status(500).json({ error: 'Server error', details: err.message });
    }
};

const changePassword = async (req, res) => {
    const { username, oldpassword, newpassword } = req.body
    if (!username || !oldpassword || !newpassword) {
        return res.json({ error: "username, oldpassword and newpassword are required" })
    }
    user = await user.findOne({ username });



}

module.exports = {
    createUser, login, changePassword

}