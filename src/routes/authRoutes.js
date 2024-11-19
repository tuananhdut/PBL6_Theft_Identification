const express = require('express');
const { createUser, login, changePassword } = require('../controllers/userController');
const router = express.Router();

router.post('/register', createUser);

router.post('/login', login);

router.put('/changepassword', changePassword);

module.exports = router