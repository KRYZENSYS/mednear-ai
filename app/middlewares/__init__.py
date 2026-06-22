"""Middleware registration and implementations."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.database import db_manager
from app.repositories import user_repository
from app.services.cache import cache_service
from app.utils.helpers import sanitize_input
from app.utils.logger import logger


class UserTrackingMiddleware(BaseMiddleware):
    """Middleware that ensures user exists in DB and tracks activity."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process update with user tracking.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Handler data.

        Returns:
            Handler result.
        """
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if not user:
            return await handler(event, data)

        try:
            async with db_manager.session() as session:
                db_user, _ = await user_repository.get_or_create(
                    session,
                    telegram_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    language_code=user.language_code or "uz",
                )
                data["db_user"] = db_user
        except Exception as e:
            logger.error(f"User tracking error: {e}", exc_info=True)

        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """Simple in-memory throttling middleware."""

    def __init__(self, rate_limit: int = 30, period: int = 60) -> None:
        """Initialize throttling.

        Args:
            rate_limit: Max requests per period.
            period: Period in seconds.
        """
        self.rate_limit = rate_limit
        self.period = period
        self.cache: dict[int, list[float]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Apply throttling.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Handler data.

        Returns:
            Handler result or None if throttled.
        """
        import time

        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.time()

        if user_id not in self.cache:
            self.cache[user_id] = []

        self.cache[user_id] = [
            ts for ts in self.cache[user_id] if now - ts < self.period
        ]

        if len(self.cache[user_id]) >= self.rate_limit:
            logger.warning(f"Throttled user_id={user_id}")
            if isinstance(event, Message):
                await event.answer("⚠️ Juda ko'p so'rovlar. Biroz kuting.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Juda ko'p so'rovlar.", show_alert=True)
            return None

        self.cache[user_id].append(now)
        return await handler(event, data)


class SanitizationMiddleware(BaseMiddleware):
    """Middleware that sanitizes text inputs."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Sanitize message text.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Handler data.

        Returns:
            Handler result.
        """
        if isinstance(event, Message) and event.text:
            data["raw_text"] = event.text
            event.text = sanitize_input(event.text)
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware that logs all updates."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Log the update.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Handler data.

        Returns:
            Handler result.
        """
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            logger.debug(f"Message from {user_id}: {event.text[:50] if event.text else '<media>'}")
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            logger.debug(f"Callback from {user_id}: {event.data}")
        return await handler(event, data)


def register_all_middlewares(dp: Dispatcher) -> None:
    """Register all middlewares on dispatcher.

    Args:
        dp: Aiogram dispatcher.
    """
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(UserTrackingMiddleware())
    dp.callback_query.middleware(UserTrackingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=30, period=60))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=60, period=60))
    dp.message.middleware(SanitizationMiddleware())
    logger.info("All middlewares registered")