import json
from typing import Any, Dict, Optional, cast

from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._utils.types import CDCData, ConversationDict, ConversationKey

class JSONPersistence(BasePersistence[Dict[Any, Any], Dict[Any, Any], Dict[Any, Any]]):
    def __init__(
        self,
        file_path: str,
        store_data: Optional[PersistenceInput] = None,
        update_interval: float = 60,
    ):
        super().__init__(store_data=store_data, update_interval=update_interval)
        self.file_path = file_path
        self._data = self.load_data()
        self.store_data = PersistenceInput(
            bot_data=False, 
            chat_data=True, 
            user_data=True, 
            callback_data=False
        )

    def load_data(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {
                "user_data": {},
                "chat_data": {},
            }
        return data

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self._data, file, indent=4)

    async def get_user_data(self) -> Dict[int, Dict[object, object]]:
        return self._data["user_data"]

    async def get_chat_data(self) -> Dict[int, Dict[object, object]]:
        return self._data["chat_data"]

    async def get_bot_data(self) -> None:
        pass

    async def get_callback_data(self) -> None:
        pass

    async def get_conversations(self, name: str) -> None:
        pass

    async def update_user_data(self, user_id: int, data: Dict[Any, Any]) -> None:
        self._data["user_data"][user_id] = data
        self.save_data()

    async def update_chat_data(self, chat_id: int, data: Dict[Any, Any]) -> None:
        self._data["chat_data"][chat_id] = data
        self.save_data()

    async def update_bot_data(self, data: Dict[Any, Any]) -> None:
        pass

    async def update_callback_data(self, data: CDCData) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        pass 

    async def drop_user_data(self, user_id: int) -> None:
        pass 

    async def refresh_user_data(self, user_id: int, user_data: Dict[Any, Any]) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: Dict[Any, Any]) -> None:
        pass

    async def refresh_bot_data(self, bot_data: Dict[Any, Any]) -> None:
        pass

    async def update_conversation(
        self, name: str, key: ConversationKey, new_state: Optional[object]
    ) -> None:
        pass

    async def flush(self) -> None:
        self.save_data()