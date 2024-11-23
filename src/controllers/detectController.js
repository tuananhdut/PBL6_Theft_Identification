const Camera = require("../models/Camera")
const Detect = require("../models/Detect")
const ApiError = require("../utils/ApiError")
const ApiSuccess = require("../utils/ApiSuccess")
const { generateUUID } = require("../utils/bcryptHelper")

const reportDetectedAction = async (req, res, next) => {
    const { cameraId, beginTime, endTime, sensitivity } = req.body
    console.log(cameraId, beginTime, endTime, sensitivity)
    if (!cameraId || !beginTime || !endTime || !sensitivity) {
        return next(new ApiError(400, "camera id, beginTime, endtime or sensitivity are require"))
    }

    if (+sensitivity < 15) {
        return next(new ApiError(400, "sensitivity must be greater than 15"))
    }

    const camera = await Camera.findOne({ cameraId })

    if (!camera) {
        return next(new ApiError(400, "camera id not found"))
    }

    const newDetect = new Detect({
        uuid: generateUUID(),
        cameraId: cameraId,
        beginTimeStamp: beginTime,
        endTimeStamp: endTime,
        sensitivity: sensitivity
    })
    try {
        newDetect.save()
        return res.status(200).json(new ApiSuccess("api success", { actionID: newDetect.uuid }))
    } catch (err) {
        next(err)
    }
}

const getDetectByUUID = async (req, res, next) => {
    try {
        const uuid = req.body.actionId

        if (!uuid) {
            return next(new ApiError(400, "uuid is require"))
        }

        const detect = await Detect.findOne({ uuid })
        return res.status(200).json(new ApiSuccess("api success", detect))
    } catch (err) {
        next(err)
    }
}

const getAllDetectByCameraID = async (req, res, next) => {
    try {
        const cameraId = req.body.cameraId

        if (!cameraId) {
            return next(new ApiError(400, "cameraid is require"))
        }

        const listDetect = await Detect.find({ cameraId })

        return res.status(200).json(new ApiSuccess("Get all detect by cameraid success", listDetect))

    } catch (err) {
        next(err)
    }
}

const uploadVideo = (req, res, next) => {

}

module.exports = {
    reportDetectedAction, getDetectByUUID, getAllDetectByCameraID, uploadVideo
}