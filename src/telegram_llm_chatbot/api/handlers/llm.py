import io
import logging
import os
from datetime import datetime

from hydra.utils import instantiate
from omegaconf import OmegaConf
from PIL import Image

from telegram_llm_chatbot.api.common import download_file, is_command, user_sign_in
from telegram_llm_chatbot.core.files import TextFileParser
from telegram_llm_chatbot.core.llm import LLM
from telegram_llm_chatbot.db import crud

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define constants
TEMP_DIR = "./.tmp/files"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
ALLOWED_TEXT_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # 10 MB

# Initialize file parser
text_file_parser = TextFileParser(max_file_size_mb=MAX_FILE_SIZE_MB, allowed_file_types=ALLOWED_TEXT_EXTENSIONS)


def register_handlers(bot):
    # Define the command for invoking the chatbot
    @bot.message_handler(func=lambda message: not is_command(message), content_types=["text", "photo", "document"])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)
        user_sign_in(user_id, message)

        last_chat_id = crud.get_last_chat_id(user_id)
        if last_chat_id is None:
            # Pick the first chat if no chat is selected
            chats = crud.get_user_chats(user_id)
            if chats:
                last_chat_id = chats[0].id
                bot.send_message(user_id, f"Are you are in the chat {chats[0].name}")
            else:
                # Create a new chat
                chat = crud.create_chat(user_id, "New chat")
                last_chat_id = chat.id
                bot.send_message(user_id, "No chat selected. Created a new chat.")
            crud.update_user_last_chat_id(user_id, last_chat_id)

        user_message = message.caption if message.caption else ""
        image = None

        if message.content_type in ["photo", "document"]:
            # Extract file information
            if message.content_type == "photo":
                file_info = message.photo[-1]
            else:  # "document"
                file_info = message.document

            file_id = file_info.file_id
            filename = getattr(file_info, "file_name", f"file_{file_id}")
            user_input_file_path = os.path.join(TEMP_DIR, str(user_id), filename)

            logger.info("User event", extra={"user_id": user_id, "user_message": user_message})

            # Ensure the directory exists
            os.makedirs(os.path.dirname(user_input_file_path), exist_ok=True)
            download_file(bot, file_id, user_input_file_path)

            # Validate file size before processing
            if os.path.getsize(user_input_file_path) > MAX_FILE_SIZE:
                bot.reply_to(message, f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_MB} MB.")
                return

            file_extension = filename.rsplit(".", 1)[-1].lower()

            try:
                if file_extension in ALLOWED_IMAGE_EXTENSIONS:
                    with open(user_input_file_path, "rb") as file_obj:
                        image_bytes = file_obj.read()
                        image = Image.open(io.BytesIO(image_bytes))
                elif file_extension in ALLOWED_TEXT_EXTENSIONS:
                    text_content = text_file_parser.extract_content(user_input_file_path)
                    user_message += f"\n{text_content}"
                else:
                    bot.reply_to(message, f"Unsupported file type: {file_extension}")
                    return
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                bot.reply_to(message, "An error occurred while processing your file.")
                return
            finally:
                # Clean up temporary file
                if os.path.exists(user_input_file_path):
                    os.remove(user_input_file_path)
        elif message.content_type == "text":
            user_message = message.text
        else:
            bot.reply_to(message, "Unsupported content type.")
            return

        # Truncate and add the message to the chat history
        user_message = user_message[:10000]
        crud.create_message(last_chat_id, "user", content=user_message, timestamp=datetime.now())

        # Retrieve chat history
        chat_history = crud.get_chat_history(last_chat_id)

        # Load configurations
        config_llm = OmegaConf.load("./src/telegram_llm_chatbot/conf/llm.yaml")
        model_config = instantiate(config_llm.custom)
        llm = LLM(model_config)
        logger.info(f"Loaded LLM model with config: {model_config.dict()}")

        if llm.config.stream:
            # Inform the user about processing
            sent_msg = bot.send_message(message.chat.id, "...")
            accumulated_response = ""

            # Generate response and send chunks
            for idx, chunk in enumerate(llm.run(chat_history, image=image)):
                accumulated_response += chunk.content
                if idx % 8 == 0:
                    try:
                        bot.edit_message_text(
                            accumulated_response, chat_id=message.chat.id, message_id=sent_msg.message_id
                        )
                    except Exception as e:
                        logger.error(f"Failed to edit message: {e}")
                        continue
        else:
            # Generate and send the final response
            response = llm.run(chat_history, image=image)
            bot.send_message(message.chat.id, response.response_content)
