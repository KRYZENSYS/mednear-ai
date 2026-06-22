"""Bot handlers registry."""

from aiogram import Dispatcher

from app.utils.logger import logger


def register_all_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers on dispatcher.

    Args:
        dp: Aiogram dispatcher.
    """
    from bot.handlers.start import router as start_router
    from bot.handlers.ai_chat import router as ai_router
    from bot.handlers.symptom import router as symptom_router
    from bot.handlers.medicine import router as medicine_router
    from bot.handlers.reminder import router as reminder_router
    from bot.handlers.appointment import router as appointment_router
    from bot.handlers.hospital import router as hospital_router
    from bot.handlers.profile import router as profile_router
    from bot.handlers.settings import router as settings_router
    from bot.handlers.premium import router as premium_router
    from bot.handlers.feedback import router as feedback_router
    from bot.handlers.media import router as media_router
    from bot.handlers.admin import router as admin_router
    from bot.handlers.errors import router as errors_router

    dp.include_router(start_router)
    dp.include_router(ai_router)
    dp.include_router(symptom_router)
    dp.include_router(medicine_router)
    dp.include_router(reminder_router)
    dp.include_router(appointment_router)
    dp.include_router(hospital_router)
    dp.include_router(profile_router)
    dp.include_router(settings_router)
    dp.include_router(premium_router)
    dp.include_router(feedback_router)
    dp.include_router(media_router)
    dp.include_router(admin_router)
    dp.include_router(errors_router)

    logger.info(f"Registered {len(dp.sub_routers)} handler routers")