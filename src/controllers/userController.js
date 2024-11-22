const express = require('express');
const User = require('../models/User');
const { createPassword, checkPassword } = require('../utils/bcryptHelper');
const { generateToken, verifyToken } = require('../utils/tokenHelper');
const ApiError = require('../utils/ApiError');
const ApiSuccess = require('../utils/ApiSuccess');

const createUser = async (req, res, next) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return next(new ApiError(400, 'Username and password are required.'))
    }

    const hashedPassword = await createPassword(password);

    const newUser = new User({
        username: username,
        password: hashedPassword
    })

    newUser.save()
        .then((User) => {
            res.status(201).json(new ApiSuccess("User created successfully"));
        })
        .catch((err) => {
            if (err.code === 11000) {
                next(new ApiError(400, "Username already exists"))
            } else {
                next(new ApiError(500, "Server error", err.message))
            }
        });
}

const login = async (req, res, next) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return next(new ApiError(400, "Username and password are required"))
    }

    try {
        const user = await User.findOne({ username });

        if (!user) {
            return next(new ApiError((404, "User not found")))
        }

        if (! await checkPassword(password, user.password)) {
            return next(new ApiError(400, "invalid Credentials"))
        }

        const access_token = generateToken({
            username: user.username,
            sensitivity: user.sensitivity
        })

        res.status(200).json(new ApiSuccess('Login successful', { token: access_token }));
    } catch (err) {
        next(new ApiError(500, "Server error", err.message))
    }
};

const changePassword = async (req, res, next) => {
    const { username, oldpassword, newpassword } = req.body;

    if (!username || !oldpassword || !newpassword) {
        next(new ApiError(400, "username, oldpassword and newpassword are required"))
    }

    try {
        const user = await User.findOne({ username });

        if (!user) {
            next(new ApiError(404, "Username doesn't exist"))
        }

        if (! await checkPassword(oldpassword, user.password)) {
            next(new ApiError(400, "Wrong password"))
        }

        user.password = await createPassword(newpassword);

        await user.save();

        return res.status(200).json(new ApiSuccess("Password changed successfully"));

    } catch (err) {
        next(new ApiError(500, "Server error", err.message))
    }
};


const getSensitivity = (req, res, next) => {
    try {
        const tokenVerify = req.user;

        if (!tokenVerify) {
            return res.status(401).json({ error: "Unauthorized: Token verification failed" });
        }

        console.log("Verified Token Data:", tokenVerify);

        res.status(200).json(new ApiSuccess("Token verified successfully", tokenVerify));
    } catch (err) {
        next(err);
    }
};



module.exports = {
    createUser, login, changePassword, getSensitivity

}