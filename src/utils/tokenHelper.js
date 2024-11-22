const jwt = require("jsonwebtoken")
const { JWT_SECRET } = require("../config/env")

const generateToken = (payload) => {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: '1h' })
}

const verifyToken = (token) => {
    return jwt.verify(token, JWT_SECRET)
}


module.exports = {
    verifyToken, generateToken
}