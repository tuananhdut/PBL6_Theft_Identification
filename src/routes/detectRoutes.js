const { reportDetectedAction, getDetectByUUID, getAllDetectByCameraID, uploadVideo } = require('../controllers/detectController')
const authMiddleware = require('../middleware/authMiddleware')
const express = require('express')
const multer = require('multer')

const detectRouter = express.Router()

var upload = multer({
    storage: multer.diskStorage({
        destination: function (req, file, cb) {
            cb(null, './public/videos');
        },
        filename: function async(req, file, cb) {
            // console.log(req)
            cb(null, file.originalname);
        },
    }),
    limits: {
        fileSize: 10 * 1024 * 1024,
        files: 1,
    }
});

detectRouter.post('/report', reportDetectedAction)

detectRouter.get('/get', authMiddleware, getDetectByUUID)

detectRouter.get('/getall', authMiddleware, getAllDetectByCameraID)

detectRouter.post('/video', upload.single('file'), uploadVideo)

module.exports = detectRouter