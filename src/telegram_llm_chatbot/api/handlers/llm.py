import io
import logging.config
import os
from datetime import datetime

from fastapi import UploadFile
from hydra.utils import instantiate
from omegaconf import OmegaConf
from PIL import Image

from telegram_llm_chatbot.core.exceptions import UnsupportedFileTypeException
from telegram_llm_chatbot.core.files import TextFileParser
from telegram_llm_chatbot.core.llm import LLM
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = os.getenv("LLM_API")

def download_file(bot, file_id, file_path):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as file:
        file.write(downloaded_file)
    return file_path

config_llm = OmegaConf.load("./src/telegram_llm_chatbot/conf/config_llm.yaml")
model_config = instantiate(config_llm.llm.config.default)
llm = LLM(model_config)

text_file_parser = TextFileParser(max_file_size_mb=10, allowed_file_types={"txt", "doc", "docx", "pdf"})

def is_command(message):
    if message.text is None:
        return False
    elif message.text.startswith("/"):
        return True
    else:
        return False

def register_handlers(bot):
    # Define the command for invoking the chatbot
    @bot.message_handler(func=lambda message: not is_command(message), content_types=['text', 'photo', 'document'])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)

        # add user to database if not already present
        if crud.get_user(user_id) is None:
            crud.upsert_user(user_id, message.chat.username)

        last_chat_id = crud.get_last_chat_id(user_id)

        if last_chat_id is None:
            # pick the first chat if no chat is selected
            chats = crud.get_user_chats(user_id)
            if chats:
                last_chat_id = chats[0].id
                crud.update_user_last_chat_id(user_id, last_chat_id)
            else:
                # Create a new chat
                bot.reply_to(message, cfg.strings.no_chats)

        image = None
        if message.content_type in ["photo", "document"]:
            user_message = message.caption if message.caption else ""
            file_id = message.photo[-1].file_id if message.content_type == "photo" else message.document.file_id
            filename = message.photo[-1].file_name if message.content_type == "photo" else message.document.file_name
            user_input_image_path = f"./.tmp/files/{user_id}/{filename}"
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            download_file(bot, file_id, user_input_image_path)
            file = open(user_input_image_path, "rb")
            file_extension = filename.rsplit(".", 1)[1].lower()
            if file_extension in {"jpg", "jpeg", "png", "gif"}:
                image_bytes = file.read()  # Read the file contents
                image = Image.open(io.BytesIO(image_bytes))  # Convert to PIL Image

            elif file_extension in {"pdf", "doc", "docx", "txt"}:
                uploaded_file = UploadFile(
                    filename=filename,
                    file=io.BytesIO(file.read()),
                    size=os.path.getsize(user_input_image_path)
                )
                text_content = text_file_parser.extract_content(uploaded_file)
                user_message += f"\n{text_content}"
            else:
                raise UnsupportedFileTypeException(f"Unsupported file type: {file_extension}")

        else:
            user_message = message.text

        # add the message to the chat history if it exists
        crud.create_message(last_chat_id, "user", content=user_message, timestamp=datetime.now())

        # get the chat history
        chat_history = crud.get_chat_history(last_chat_id)

        if llm.config.stream:
            # Start with an empty message
            sent_msg = bot.send_message(message.chat.id, "...")

            # Initialize an empty string to accumulate the response
            accumulated_response = ""
            # Generate response using the LLM model and send chunks as they come
            for chunk in llm.run(chat_history, image=image):
                accumulated_response += chunk.content

                try:
                    # Edit the message with the accumulated response
                    bot.edit_message_text(accumulated_response, chat_id=message.chat.id, message_id=sent_msg.message_id)
                except Exception:
                    continue
        else:
            # Generate response using the LLM model
            response = llm.run(chat_history, image=image)
            bot.send_message(message.chat.id, response.response_content)
