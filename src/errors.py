class ConfigError(Exception):
    code: str = "CONFIG_ERROR"
    retryable: bool = False

    def __init__(self, message: str, missing_key: str | None = None):
        self.message = message
        self.missing_key = missing_key
        super().__init__(message)
