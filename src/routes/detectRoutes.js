const express = require('express')
const { reportDetectedAction, getDetectByUUID, getAllDetectByCameraID, uploadVideo } = require('../controllers/detectController')
const authMiddleware = require('../middleware/authMiddleware')
const detectRouter = express.Router()

detectRouter.post('/report', reportDetectedAction)

detectRouter.get('/get', authMiddleware, getDetectByUUID)

detectRouter.get('/getall', authMiddleware, getAllDetectByCameraID)

detectRouter.post('/video', uploadVideo)

module.exports = detectRouter