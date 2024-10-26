from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class Message(BaseModel):  # noqa: D101
    chat_id: str
    role: str
    content: str
    timestemp: datetime


class User(BaseModel):  # noqa: D101
    id: int
    name: str


class Chat(BaseModel):  # noqa: D101
    user_id: int
    chat_id: int
    chat_name: str


class AddUserRequest(BaseModel):  # noqa: D101
    user: User


class AddChatRequest(BaseModel):  # noqa: D101
    user_id: int
    chat_name: str


class DeleteChatRequest(BaseModel):  # noqa: D101
    user_id: int
    chat_id: int


class DeleteChatResponse(BaseModel):  # noqa: D101
    chat_id: int


class GetChatsRequest(BaseModel):  # noqa: D101
    user_id: int


class GetChatsResponse(BaseModel):  # noqa: D101
    chats: list[Chat]


class ModelConfig(BaseModel):  # noqa: D101
    model_name: Optional[str] = None
    provider: Optional[str] = None
    max_tokens: Optional[int] = None
    chat_history_limit: int = 10
    temperature: float = 0.5
    stream: Optional[bool] = True


class ModelResponse(BaseModel):  # noqa: D101
    response_content: str
    config: ModelConfig


class DalleConfig(BaseModel):  # noqa: D101
    model_name: Optional[str] = "dall-e-2"  # The name of the model to use for image generation
    n: Optional[int] = 1  # Number of images to generate
    quality: Literal["standard", "hd"] = "standard"  # The quality of the generated images
    size: Optional[str] = "1024x1024"  # The size of the generated images


class DalleResponse(BaseModel):  # noqa: D101
    response_content: list[dict[str, str]]
    config: Optional[DalleConfig] = None
