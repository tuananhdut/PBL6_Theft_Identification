const mongoose = require('mongoose')

const DetectSchema = mongoose.Schema({
    uuid: { type: String, required: true, unique: true },
    cameraId: { type: String, required: true },
    beginTimeStamp: { type: Number, required: true },
    endTimeStamp: { type: Number, required: true },
    statusCode: { type: Number, enum: [0, 1, 2], default: 0 }
})

module.exports = mongoose.model("Detect", DetectSchema)