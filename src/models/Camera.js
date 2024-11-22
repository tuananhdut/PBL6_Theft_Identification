const mongoose = require('mongoose')
const CameraStatusCode = require('../utils/CameraStatusCode')

const CameraSchema = mongoose.Schema({
    cameraId: { type: String, required: true, unique: true },
    cameraName: { type: String, default: "" },
    username: { type: String, default: "" },
    linkingCode: { type: String, required: true, unique: true },
    status: { type: Number, enum: Object.values(CameraStatusCode), defaults: CameraStatusCode.UNKNOWN }
})
module.exports = mongoose.model("Camera", CameraSchema)