const express = require('express')
const router = express.Router();

const authRoutes = require('./userRoutes')
const cameraRouter = require('./cameraRoutes');
const detectRouter = require('./detectRoutes');

router.use('/auth', authRoutes)

router.use('/camera', cameraRouter)

router.use('/detect', detectRouter)

module.exports = router