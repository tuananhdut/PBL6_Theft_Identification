const jwt = require('jsonwebtoken');
const User = require('../models/User');
const secret = process.env.JWT_SECRET;

const validateUser = async (req, res, next) => {
    const { username, password } = req.body
    if (!username || !password) {
        return res.status(400).json({ error: "this is required" })
    }
    const user = await User.findOne({ username })
    try {
        if (!user) {
            return res.status(404).json({ error: "user not found" })
        }
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ error: "password fail" })
        }
    } catch (err) {
        return res.status(500).json({ error: 'Server error', details: err.message });
    }
    next()
}



const authenticate = (req, res, next) => {
    const token = req.header('Authorization');
    if (!token) return res.status(401).send('Access Denied');

    try {
        const verified = jwt.verify(token, secret);
        req.user = verified;
        next();
    } catch (err) {
        res.status(400).send('Invalid Token');
    }
};

module.exports = { authenticate, validateUser };
