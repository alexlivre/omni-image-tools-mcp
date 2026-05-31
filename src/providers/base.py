"""Vision Provider base class and ABC."""

from abc import ABC, abstractmethod
from typing import Any


class VisionProvider(ABC):
    """Abstract base class for vision providers."""

    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    async def analyze(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """
        Analyze an image with a custom prompt.

        Args:
            image_data: Raw image bytes
            prompt: The prompt/question about the image
            model: Optional model override

        Returns:
            Text response from the vision model
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is accessible and working."""

    def validate_image(self, image_data: bytes) -> tuple[bool, str]:
        """
        Validate image data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not image_data:
            return False, "Image data is empty"

        if len(image_data) > 10 * 1024 * 1024:
            return False, f"Image too large: {len(image_data)} bytes (max 10MB)"

        return True, ""
