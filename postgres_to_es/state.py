import abc
import datetime
import json
from typing import Any, Optional

from redis import Redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis, redis_db: str) -> None:
        self.redis_adapter = redis_adapter
        self.redis_db = redis_db

    def save_state(self, state: dict) -> None:
        self.redis_adapter.set(self.redis_db, json.dumps(state))

    def retrieve_state(self) -> dict:
        state = self.redis_adapter.get(self.redis_db)
        state = json.loads(state) if state else {}
        return state


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        state = self.storage.retrieve_state()
        state[key] = value.isoformat()
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        state = self.storage.retrieve_state()
        state = state.get(key)
        if state:
            state = datetime.datetime.fromisoformat(state)
        return state
