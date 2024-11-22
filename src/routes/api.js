const express = require('express')
const router = express.Router();

const authRoutes = require('./userRoutes')
const cameraRouter = require('./cameraRoutes')

router.use('/auth', authRoutes)
router.use('/camera', cameraRouter)

module.exports = router