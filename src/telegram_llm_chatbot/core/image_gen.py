from openai import OpenAI

from telegram_llm_chatbot.api.schemas import DalleConfig


class Dalle3OpenAI:
    """Wrapper class for the OpenAI DALL-E model."""

    def __init__(self, config: DalleConfig):
        """Initialize the DALL-E model."""
        self.config = config
        self.client = OpenAI()

    def update_config(self, config: DalleConfig) -> None:
        """Update the configuration of the model."""
        for attr in ["model_name", "n", "quality", "size"]:
            if getattr(config, attr) is not None:
                self.config.__setattr__(attr, getattr(config, attr))

    def invoke(self, prompt: str, image_size: str = None) -> str:
        """Generate an image from the model."""
        response = self.client.images.generate(
            model=self.config.model_name,
            prompt=prompt,
            size=image_size,
            quality=self.config.quality,
            n=self.config.n,
        )
        return response.data[0].url
