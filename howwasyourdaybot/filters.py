from telegram import Message
from telegram.ext.filters import MessageFilter
import logging

from phrases_multilang import translated_emotion_to_key


class FilterAllowedChats(MessageFilter):
    def __init__(self, allowed_chat_ids):
        super().__init__()
        self.allowed_chat_ids = allowed_chat_ids

    def filter(self, message: Message) -> bool:
        if len(self.allowed_chat_ids) == 0:
            # if allowed chat ids string is empty then everyone can use the bot
            return True
        else:
            chat_id = message.chat.id
            is_allowed = chat_id in self.allowed_chat_ids
            if not is_allowed:
                logging.error(f"chat_id={chat_id} is not allowed")
            return is_allowed


class FilterEmotions(MessageFilter):
    def __init__(self, emotions_list):
        super().__init__()
        self.emotions_list = emotions_list

    def filter(self, message: Message) -> bool:
        # handle translated emotions
        text = translated_emotion_to_key(message.text)
        chat_id = str(message.chat.id)
        is_known_emotion = text in self.emotions_list.keys()
        if not is_known_emotion:
            logging.error(f"Emotion {text}/{message.text} is not known (chat_id={chat_id})")
        return is_known_emotion


class FilterIsDigit(MessageFilter):
    def __init__(self):
        super().__init__()

    def filter(self, message: Message) -> bool:
        text = message.text
        chat_id = str(message.chat.id)
        try:
            float(text)
            logging.info(f"Got {text}, which is a number (chat_id={chat_id}).")
            return True
        except (ValueError, TypeError):
            logging.info(f"Got {text}, which is not a number (chat_id={chat_id}).")
            return False
