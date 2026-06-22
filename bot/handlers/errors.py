"""Global error handler."""

from aiogram import Router
from aiogram.types import ErrorEvent

from app.utils.logger import logger

router = Router(name="errors")


@router.errors()
async def error_handler(event: ErrorEvent) -> None:
    """Handle errors globally.

    Args:
        event: Error event.
    """
    logger.error(
        f"Error in handler: {event.exception}",
        exc_info=event.exception,
    )
    try:
        if event.update.message:
            await event.update.message.answer(
                "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n"
                "/start - botni qayta ishga tushirish"
            )
        elif event.update.callback_query:
            await event.update.callback_query.answer(
                "❌ Xatolik yuz berdi.",
                show_alert=True,
            )
    except Exception:
        pass