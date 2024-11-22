const ApiError = require('../utils/ApiError');
const { verifyToken } = require('../utils/tokenHelper');

const authMiddleware = (req, res, next) => {
    const authHeader = req.headers['authorization'];

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return next(new ApiError(401, "Authorization token missing or invalid"));
    }

    const token = authHeader.split(" ")[1];

    try {
        const decoded = verifyToken(token)
        req.user = decoded;
        next();
    } catch (err) {
        next(new ApiError(401, "Invalid or expired token"));
    }
};

module.exports = authMiddleware;
