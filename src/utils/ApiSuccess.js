class ApiSuccess {
    constructor(message, data = null) {
        this.success = true
        this.message = message
        this.data = data
    }
}

module.exports = ApiSuccess