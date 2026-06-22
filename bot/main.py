"""Main bot entry point.

This module initializes and runs the MedNear AI Telegram bot.
"""

import asyncio
import signal
import sys
from contextlib import suppress
from typing import NoReturn

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

from app.config import settings
from app.database import db_manager
from app.database.models import *  # noqa: F401,F403 - register models
from app.handlers import register_all_handlers
from app.middlewares import register_all_middlewares
from app.services.cache import cache_service
from app.services.notification import notification_service
from app.services.scheduler import scheduler_service
from app.utils.logger import logger, setup_logging


async def set_bot_commands(bot: Bot) -> None:
    """Set bot commands menu.

    Args:
        bot: Bot instance.
    """
    private_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="menu", description="Asosiy menyu"),
        BotCommand(command="chat", description="AI bilan suhbat"),
        BotCommand(command="symptom", description="Alomatlarni tekshirish"),
        BotCommand(command="medicine", description="Dori qidirish"),
        BotCommand(command="reminder", description="Eslatmalar"),
        BotCommand(command="appointment", description="Qabulga yozilish"),
        BotCommand(command="hospital", description="Kasalxona qidirish"),
        BotCommand(command="profile", description="Profilim"),
        BotCommand(command="settings", description="Sozlamalar"),
        BotCommand(command="premium", description="Premium obuna"),
        BotCommand(command="language", description="Tilni o'zgartirish"),
        BotCommand(command="feedback", description="Fikr-mulohaza"),
        BotCommand(command="cancel", description="Bekor qilish"),
    ]

    group_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="chat", description="AI bilan suhbat"),
    ]

    try:
        await bot.set_my_commands(
            private_commands,
            scope=BotCommandScopeAllPrivateChats(),
        )
        await bot.set_my_commands(
            group_commands,
            scope=BotCommandScopeAllGroupChats(),
        )
        logger.info(f"Set {len(private_commands)} private and {len(group_commands)} group commands")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")


async def on_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    """Execute on bot startup.

    Args:
        bot: Bot instance.
        dispatcher: Dispatcher instance.
    """
    logger.info("=" * 50)
    logger.info(f"Starting {settings.app.name} v{settings.app.version}")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Database: {settings.db.host}:{settings.db.port}/{settings.db.name}")
    logger.info("=" * 50)

    try:
        await cache_service.connect()
        logger.info("Cache service connected")
    except Exception as e:
        logger.warning(f"Cache service failed to connect: {e}")

    try:
        bot_info = await bot.get_me()
        logger.info(
            f"Bot authorized as @{bot_info.username} "
            f"(id={bot_info.id}, name={bot_info.first_name})"
        )
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        raise

    await set_bot_commands(bot)

    try:
        if not settings.is_production():
            await db_manager.create_all()
            logger.info("Database tables created (development mode)")
    except Exception as e:
        logger.warning(f"Database init: {e}")

    try:
        await scheduler_service.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler failed to start: {e}")

    for admin_id in settings.bot.admin_id_list:
        try:
            await bot.send_message(
                admin_id,
                f"🚀 <b>{settings.app.name} started!</b>\n\n"
                f"Environment: <code>{settings.app.environment}</code>\n"
                f"Version: <code>{settings.app.version}</code>\n"
                f"Time: <code>{__import__('datetime').datetime.utcnow().isoformat()}</code>",
            )
        except Exception as e:
            logger.debug(f"Could not notify admin {admin_id}: {e}")


async def on_shutdown(bot: Bot, dispatcher: Dispatcher) -> None:
    """Execute on bot shutdown.

    Args:
        bot: Bot instance.
        dispatcher: Dispatcher instance.
    """
    logger.info("Shutting down bot...")

    try:
        await scheduler_service.stop()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.warning(f"Scheduler stop error: {e}")

    try:
        await cache_service.disconnect()
        logger.info("Cache service disconnected")
    except Exception as e:
        logger.warning(f"Cache disconnect error: {e}")

    try:
        await db_manager.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Database close error: {e}")

    try:
        await bot.session.close()
        logger.info("Bot session closed")
    except Exception as e:
        logger.warning(f"Bot session close error: {e}")

    for admin_id in settings.bot.admin_id_list:
        try:
            await bot.send_message(
                admin_id,
                f"⏹ <b>{settings.app.name} stopped.</b>",
            )
        except Exception:
            pass

    logger.info("=" * 50)
    logger.info(f"{settings.app.name} shutdown complete")
    logger.info("=" * 50)


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher.

    Returns:
        Configured Dispatcher instance.
    """
    try:
        storage = RedisStorage.from_url(
            settings.redis.url,
            key_builder=None,
        )
        logger.info("Using Redis storage for FSM")
    except Exception as e:
        logger.warning(f"Redis storage unavailable ({e}), using memory storage")
        storage = MemoryStorage()

    dp = Dispatcher(
        storage=storage,
        name=settings.bot.username,
        debug=settings.bot.debug,
    )

    register_all_middlewares(dp)
    register_all_handlers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return dp


async def main() -> NoReturn:
    """Main entry point.

    Starts the bot using long polling or webhook based on settings.
    """
    setup_logging()
    logger.info(f"Initializing {settings.app.name}...")

    try:
        bot = Bot(
            token=settings.bot.token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                disable_notification=False,
                protect_content=False,
                link_preview_options=None,
            ),
        )
        logger.info("Bot instance created")
    except Exception as e:
        logger.critical(f"Failed to create bot: {e}", exc_info=True)
        sys.exit(1)

    dp = create_dispatcher()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler() -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            pass

    use_webhook = bool(settings.bot.webhook_url)

    try:
        if use_webhook:
            logger.info(f"Starting in WEBHOOK mode at {settings.bot.webhook_url}")
            await dp.start_webhook(
                bot=bot,
                webhook_path="/webhook",
                webhook_url=settings.bot.webhook_url,
                port=settings.bot.webhook_port,
                allowed_updates=dp.resolve_used_update_types(),
            )
        else:
            logger.info("Starting in POLLING mode...")
            allowed_updates = dp.resolve_used_update_types()
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(
                bot,
                allowed_updates=allowed_updates,
                polling_timeout=30,
                handle_signals=True,
                close_bot_session=True,
            )
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        with suppress(Exception):
            await on_shutdown(bot, dp)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)