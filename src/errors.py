from typing import Any
from enum import Enum


class ErrorCode(Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MODEL_NOT_ALLOWED = "MODEL_NOT_ALLOWED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"


class OmniVisionError(Exception):
    code: ErrorCode = ErrorCode.VALIDATION_ERROR
    message: str = "An error occurred"
    retryable: bool = False
    details: dict[str, Any] | None = None

    def __init__(
        self,
        message: str | None = None,
        code: ErrorCode | None = None,
        retryable: bool | None = None,
        details: dict[str, Any] | None = None,
    ):
        if message:
            self.message = message
        if code:
            self.code = code
        if retryable is not None:
            self.retryable = retryable
        if details:
            self.details = details

        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "retryable": self.retryable,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class ValidationError(OmniVisionError):
    code = ErrorCode.VALIDATION_ERROR
    retryable = False


class ModelNotAllowedError(ValidationError):
    code = ErrorCode.MODEL_NOT_ALLOWED

    def __init__(self, model: str, allowed_models: list[str]):
        super().__init__(
            message=f"Model '{model}' not in allowed list",
            details={"model": model, "allowed_models": allowed_models},
        )


class FileNotFoundError(OmniVisionError):
    code = ErrorCode.FILE_NOT_FOUND

    def __init__(self, path: str):
        super().__init__(
            message=f"File not found: {path}",
            details={"path": path},
        )


class ImageTooLargeError(OmniVisionError):
    code = ErrorCode.IMAGE_TOO_LARGE
    retryable = False

    def __init__(self, size_bytes: int, max_bytes: int = 10 * 1024 * 1024):
        size_mb = size_bytes / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        super().__init__(
            message=f"Image size ({size_mb:.1f}MB) exceeds maximum ({max_mb:.1f}MB)",
            details={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )


class UnsupportedFormatError(OmniVisionError):
    code = ErrorCode.UNSUPPORTED_FORMAT
    retryable = False

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".heif"}

    def __init__(self, format: str):
        super().__init__(
            message=f"Unsupported image format: {format}",
            details={"format": format, "supported": list(self.SUPPORTED_FORMATS)},
        )


class ProviderError(OmniVisionError):
    code = ErrorCode.PROVIDER_ERROR
    retryable = True


class TimeoutError(ProviderError):
    code = ErrorCode.TIMEOUT_ERROR

    def __init__(self, seconds: int):
        super().__init__(
            message=f"Request timed out after {seconds} seconds",
            details={"timeout_seconds": seconds},
        )


class RateLimitError(ProviderError):
    code = ErrorCode.RATE_LIMIT_ERROR

    def __init__(self, retry_after: int | None = None):
        super().__init__(
            message="Rate limit exceeded",
            retryable=True,
            details={"retry_after_seconds": retry_after} if retry_after else None,
        )


class ConfigError(OmniVisionError):
    code = ErrorCode.CONFIG_ERROR
    retryable = False

    def __init__(self, message: str, missing_key: str | None = None):
        super().__init__(
            message=message,
            details={"missing_key": missing_key} if missing_key else None,
        )
