require('dotenv').config()

const HOST = process.env.HOST || "127.0.0.1"
const PORT = process.env.PORT || "3999"
const MONGOURI = process.env.MONGOURI
const JWT_SECRET = process.env.JWT_SECRET

module.exports = {
    HOST, PORT, MONGOURI, JWT_SECRET
}
