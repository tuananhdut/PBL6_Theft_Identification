const express = require('express')
const { cameraRegister, deleteCamera, getcamera, linkCamera, renameCamera, getAllCameraByCameraName } = require('../controllers/cameraController')
const authMiddleware = require('../middleware/authMiddleware')
const cameraRouter = express.Router()

cameraRouter.get('/register', cameraRegister)

cameraRouter.delete('/delete', authMiddleware, deleteCamera)

cameraRouter.get('/get', authMiddleware, getcamera)

cameraRouter.post('/link', authMiddleware, linkCamera)

cameraRouter.post('/rename', renameCamera)

cameraRouter.get('/getall', authMiddleware, getAllCameraByCameraName)


module.exports = cameraRouter