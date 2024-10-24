from openai import OpenAI
from llm_chatbot_api.api.schemas import ImageModelConfig, ImageModelResponse

class Dalle3OpenAI:
    def __init__(self, config: ImageModelConfig):
        self.config = config
        self.client = OpenAI()

    def update_config(self, config: ImageModelConfig) -> None:
        for attr in ['model_name', 'n', 'quality', 'size']:
            if getattr(config, attr) is not None:
                self.config.__setattr__(attr, getattr(config, attr))

    def generate_image(self, prompt: str) -> str:
        response = self.client.images.generate(
            model=self.config.model_name,
            prompt=prompt,
            size=self.config.size,
            quality=self.config.quality,
            n=self.config.n
        )
        return response.data[0].url
