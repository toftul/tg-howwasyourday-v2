from telegram import Message
from telegram.ext.filters import MessageFilter
import logging

class FilterAllowedChats(MessageFilter):
    def __init__(self, allowed_chat_ids):
        super().__init__()
        self.allowed_chat_ids = allowed_chat_ids

    def filter(self, message: Message) -> bool:
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
        text = message.text
        chat_id = str(message.chat.id)
        is_known_emotion = text in self.emotions_list.keys()
        if not is_known_emotion:
            logging.error(f"Emotion {text} is not known (chat_id={chat_id})")
        return is_known_emotion


class FilterIsDigit(MessageFilter):
    def __init__(self):
        super().__init__()

    def filter(self, message: Message) -> bool:
        text = message.text
        chat_id = str(message.chat.id)
        # check if it is a number
        # https://stackoverflow.com/a/23639915/10282471
        isdigit = text.replace('.','',1).replace('-','',1).replace('+','',1).isdigit()
        if not isdigit:
            logging.info(f"Got {text}, which is not a number (chat_id={chat_id}).")
        else: 
            logging.info(f"Got {text}, which is a number (chat_id={chat_id}).")
        return isdigit