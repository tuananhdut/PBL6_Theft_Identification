const express = require('express');
const { createUser, login, changePassword, getSensitivity } = require('../controllers/userController');
const authMiddleware = require('../middleware/authMiddleware');
const router = express.Router();

router.post('/register', createUser);

router.post('/login', login);

router.put('/changepassword', changePassword);

router.get('/sensitivity', authMiddleware, getSensitivity)

module.exports = router