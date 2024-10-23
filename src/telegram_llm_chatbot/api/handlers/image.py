import os
import logging.config
import requests
from omegaconf import OmegaConf
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

def is_command(message):
    if message.text is None:
        return False
    elif message.text.startswith("/"):
        return True
    else:
        return False

def register_handlers(bot):
                
    @bot.message_handler(commands=["generate"])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)

        if crud.get_user(user_id) is None:
            crud.upsert_user(user_id, message.chat.username)

        response = requests.get(f"{base_url}/users/users/{user_id}")
        if response.status_code == 404:
            response = requests.post(
                f"{base_url}/users",
                json={"user": {"id": user_id, "name": message.chat.username}}
            )
            if response.status_code == 200:
                logger.info(f"User with id {user_id} added successfully.")
            else:
                logger.error(f"Error adding user with id {user_id}: {response.json()['message']}")

        last_chat_id = crud.get_last_chat_id(user_id)

        if last_chat_id is None:
            bot.reply_to(message, cfg.strings.no_chats)
            return

        bot.reply_to(message, "Please provide a description for the image:")
        
        # Register a new handler to capture the user's description
        def handle_description(message):
            user_message = message.text
            user_id = message.chat.id
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            data = {"user_id": user_id, "user_message": user_message}
            response = requests.post(f"{base_url}/image/generate", data=data)
            if response.status_code == 200:
                response_content = response.json()['model_response']['response_content'][0]["image_url"]
                image_response = requests.get(response_content)
                if image_response.status_code == 200:
                    bot.send_chat_action(chat_id=user_id, action="upload_photo")
                    bot.send_photo(chat_id=user_id, photo=image_response.content)
                else:
                    bot.reply_to(message, "Error downloading the image.")
            else:
                bot.reply_to(message, f"Error generating image: {response.json()['message']}")
            
        bot.register_next_step_handler(message, handle_description)

