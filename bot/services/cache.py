from typing import List

from fluent.runtime import FluentLocalization
from redis.asyncio import Redis


class Cache:
    def __init__(self, redis: Redis, languages: List[FluentLocalization]):
        self.redis = redis
        self.languages = languages

    async def get_language(
        self, user_id: int, lang_only: bool = False
    ) -> str | FluentLocalization:
        language = await self.redis.get(f"user_language:{user_id}")
        if not language:
            language = "ru"
        if lang_only:
            return language
        return self.get_l10n(language)

    async def set_user_language(self, user_id: int, language: str):
        await self.redis.set(f"user_language:{user_id}", language)

    def get_l10n(self, language: str = "ru") -> FluentLocalization:
        return self.languages[language]

    async def acquire_lock(
        self, lock_key: str, user_id: int, value: str = None, timeout: int = 1
    ) -> bool:
        """Попытка захватить блокировку в Redis."""
        lock_value = value or str(user_id)
        return bool(await self.redis.set(lock_key, lock_value, nx=True, ex=timeout))

    async def release_lock(self, lock_key: str):
        """Освобождение блокировки в Redis."""
        await self.redis.delete(lock_key)

    async def lock(
        self, lock_key: str, user_id: int, value: int = None, timeout: int = 1
    ):
        """Контекстный менеджер для захвата и освобождения блокировки."""
        return RedisLock(self, lock_key, user_id, value, timeout)


class RedisLock:
    def __init__(
        self, cache: Cache, lock_key: str, user_id: int, value: int, timeout: int
    ):
        self.cache = cache
        self.lock_key = lock_key
        self.user_id = user_id
        self.value = value
        self.timeout = timeout
        self.lock_acquired = False

    async def __aenter__(self):
        self.lock_acquired = await self.cache.acquire_lock(
            self.lock_key, self.user_id, self.value, self.timeout
        )
        if not self.lock_acquired:
            raise CustomLockError("Не удалось захватить блокировку.")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.lock_acquired:
            await self.cache.release_lock(self.lock_key)


class CustomLockError(Exception):
    pass
