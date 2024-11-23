const jwt = require("jsonwebtoken")
const { JWT_SECRET } = require("../config/env")
const bcrypt = require('bcryptjs');
const crypto = require('crypto');


const generateUUID = () => {
    return crypto.randomUUID()
}

const createPassword = async (password) => {
    return await bcrypt.hash(password, 10);
}

const generateCameraId = () => {
    return crypto.randomBytes(4).toString('hex'); // 4 byte => 8 ký tự
};

const generateLinkingCode = () => {
    return crypto.randomBytes(3).toString('hex'); // 4 byte => 8 ký tự
};

const checkPassword = async (password, checkpass) => {
    return await bcrypt.compare(password, checkpass)
}

module.exports = {
    checkPassword, createPassword, generateCameraId, generateLinkingCode, generateUUID
}