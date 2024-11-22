const jwt = require("jsonwebtoken")
const { JWT_SECRET } = require("../config/env")
const bcrypt = require('bcryptjs');


const createPassword = async (password) => {
    return await bcrypt.hash(password, 10);
}

const checkPassword = async (password, checkpass) => {
    return await bcrypt.compare(password, checkpass)
}

module.exports = {
    checkPassword, createPassword
}