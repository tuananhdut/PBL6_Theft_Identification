require('dotenv').config()
const express = require('express')
const apiRouter = require('./routes/api')
const bodyParser = require('body-parser')
const connectDB = require('./config/database')
const errorMiddleware = require('./middleware/errorMiddleware')
const { HOST, PORT } = require('./config/env')

const app = express()

//body parser
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())

// static file url: http://localhost:3999/static/
app.use('/static', express.static('public'))

connectDB();

app.use('/', apiRouter)

app.use(errorMiddleware)

app.listen(PORT, HOST, () => {
    console.log(`http://${HOST}:${PORT}`)
})