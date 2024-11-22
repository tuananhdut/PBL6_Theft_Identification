const Camera = require("../models/Camera");
const User = require("../models/User");
const ApiError = require("../utils/ApiError");
const ApiSuccess = require("../utils/ApiSuccess")
const { generateCameraId, generateLinkingCode } = require("../utils/bcryptHelper")


const cameraRegister = (req, res, next) => {
    const cameraId = generateCameraId();
    const linkingCode = generateLinkingCode();

    const camera = new Camera({
        cameraId: cameraId,
        linkingCode: linkingCode
    });

    camera.save()
        .then(() => {
            return res.status(201).json(new ApiSuccess("register camera success", { cameraId: camera.cameraId, linkingCode: camera.linkingCode }));
        })
        .catch((err) => {
            next(new ApiError(500, "Failed to register camera", err.message))
        });
};

const deleteCamera = async (req, res, next) => {
    try {
        const cameraId = req.body.cameraId;

        const isCameraId = await Camera.findOne({ cameraId });
        if (!isCameraId) {
            return next(new ApiError(400, "cameraId not found"));
        }

        await Camera.deleteOne({ cameraId });

        return res.status(200).json({ message: "Camera deleted successfully" });

    } catch (err) {
        return next(err);
    }
};


const getcamera = async (req, res, next) => {
    try {
        const cameraId = req.body.cameraId;

        const camera = await Camera.findOne({ cameraId });
        if (!camera) {
            return next(new ApiError(400, "cameraId not found"));
        }

        return res.status(200).json(new ApiSuccess("camera", { cameraId: camera.cameraId, cameraName: camera.cameraName, username: camera.username, status: camera.status }));
    } catch (err) {
        next(err)
    }
}

const linkCamera = async (req, res, next) => {
    try {
        const { username } = req.user
        const linkingCode = req.body.linkingCode
        if (!linkingCode) {
            return next(new ApiError(400, "linkingCode is require"))
        }

        const camera = await Camera.findOne({ linkingCode })
        if (!camera) {
            return next(new ApiError(400, "camera not found"))
        }

        const checkUser = await User.findOne({ username })
        if (!checkUser) {
            return next(new ApiError(400, "user not found"))
        }
        const updateCamera = await Camera.findOneAndUpdate(
            { linkingCode },
            { $set: { username: username } },
            { new: true }
        )
        return res.status(200).json(new ApiSuccess("Link camera with user success"))

    } catch (err) {
        next(err)
    }
}

const renameCamera = async (req, res, next) => {
    try {
        const { cameraId, name } = req.body
        if (!cameraId && !name) {
            return next(new ApiError(400, "camera or newname are require"))
        }
        const camera = await Camera.findOne({ cameraId })
        if (!camera) {
            return next(new ApiError(400, "Camera Id not found"))
        }

        await Camera.findOneAndUpdate(
            { cameraId },
            { $set: { cameraName: name } }
        )
        return res.status(200).json(new ApiSuccess("rename success"))

    } catch (err) {
        next(err)
    }
}

module.exports = {
    cameraRegister, deleteCamera, getcamera, linkCamera, renameCamera
}