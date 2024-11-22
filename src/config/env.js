require('dotenv').config()

const HOST = process.env.HOST
const PORT = process.env.PORT
const MONGOURI = process.env.MONGOURI
const JWT_SECRET = process.env.JWT_SECRET

module.exports = {
    HOST, PORT, MONGOURI, JWT_SECRET
}
