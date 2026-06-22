"""Notification service for sending push notifications."""

from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from app.config import settings
from app.utils.logger import logger


class NotificationService:
    """Service for sending notifications to users.

    Handles push notifications, scheduled messages, broadcast campaigns.
    """

    def __init__(self) -> None:
        """Initialize notification service."""
        self._bot: Bot | None = None

    def set_bot(self, bot: Bot) -> None:
        """Set bot instance.

        Args:
            bot: Aiogram Bot instance.
        """
        self._bot = bot
        logger.info("Notification service bot set")

    async def send_to_user(
        self,
        user_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        parse_mode: str = "HTML",
    ) -> bool:
        """Send message to user.

        Args:
            user_id: Telegram user ID.
            text: Message text.
            reply_markup: Optional inline keyboard.
            parse_mode: Parse mode (HTML/Markdown).

        Returns:
            True if sent successfully.
        """
        if not self._bot:
            logger.error("Bot not set in notification service")
            return False
        try:
            await self._bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
            return False

    async def broadcast(
        self,
        user_ids: list[int],
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> dict[str, int]:
        """Broadcast message to multiple users.

        Args:
            user_ids: List of user IDs.
            text: Message text.
            reply_markup: Optional inline keyboard.

        Returns:
            Stats dict with success/failure counts.
        """
        success = 0
        failed = 0
        for user_id in user_ids:
            if await self.send_to_user(user_id, text, reply_markup):
                success += 1
            else:
                failed += 1
        logger.info(f"Broadcast complete: {success} success, {failed} failed")
        return {"success": success, "failed": failed}

    async def send_reminder(
        self,
        user_id: int,
        medicine_name: str,
        dosage: str,
        instructions: str | None = None,
    ) -> bool:
        """Send medicine reminder.

        Args:
            user_id: Telegram user ID.
            medicine_name: Name of medicine.
            dosage: Dosage string.
            instructions: Optional instructions.

        Returns:
            True if sent.
        """
        text = (
            f"⏰ <b>Dori eslatmasi</b>\n\n"
            f"💊 <b>{medicine_name}</b>\n"
            f"📏 Doza: {dosage}\n"
        )
        if instructions:
            text += f"📋 {instructions}\n"
        text += f"\n⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}"

        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qildim", callback_data=f="med_taken:{medicine_name}"),
                InlineKeyboardButton(text="⏰ 10 daqiqadan so'ng", callback_data="med_snooze"),
            ]
        ])

        return await self.send_to_user(user_id, text, reply_markup=keyboard)


notification_service = NotificationService()