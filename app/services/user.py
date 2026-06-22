"""User service - business logic for user operations."""

from datetime import datetime
from typing import Any

from app.database import db_manager
from app.database.enums import Language, UserRole
from app.repositories import user_repository
from app.utils.helpers import generate_referral_code
from app.utils.logger import logger


class UserService:
    """Business logic service for user operations."""

    async def get_or_create_user(
        self,
        telegram_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        language_code: str = "uz",
        referral_code: str | None = None,
    ) -> tuple[Any, bool]:
        """Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID.
            first_name: First name.
            last_name: Last name.
            username: Username.
            language_code: Telegram language code.
            referral_code: Referral code.

        Returns:
            Tuple of (User, created).
        """
        async with db_manager.session() as session:
            return await user_repository.get_or_create(
                session,
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language_code=language_code,
                referral_code=referral_code,
            )

    async def change_language(
        self, telegram_id: int, language: Language
    ) -> bool:
        """Change user's language.

        Args:
            telegram_id: Telegram user ID.
            language: New language.

        Returns:
            True if changed.
        """
        try:
            async with db_manager.session() as session:
                user = await user_repository.get_by_telegram_id(session, telegram_id)
                if user:
                    user.language = language
                    await session.flush()
                    logger.info(f"User {telegram_id} language changed to {language}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Change language error: {e}", exc_info=True)
            return False

    async def update_activity(self, telegram_id: int) -> None:
        """Update user last activity.

        Args:
            telegram_id: Telegram user ID.
        """
        try:
            async with db_manager.session() as session:
                user = await user_repository.get_by_telegram_id(session, telegram_id)
                if user:
                    user.last_activity_at = datetime.utcnow()
                    await session.flush()
        except Exception as e:
            logger.warning(f"Activity update error: {e}")

    async def promote_to_admin(
        self, telegram_id: int, role: UserRole = UserRole.ADMIN
    ) -> bool:
        """Promote user to admin.

        Args:
            telegram_id: Telegram user ID.
            role: New role.

        Returns:
            True if promoted.
        """
        try:
            async with db_manager.session() as session:
                user = await user_repository.get_by_telegram_id(session, telegram_id)
                if user:
                    user.role = role
                    await session.flush()
                    logger.info(f"User {telegram_id} promoted to {role}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Promote error: {e}")
            return False

    async def ban_user(
        self, telegram_id: int, reason: str, until: datetime | None = None
    ) -> bool:
        """Ban a user.

        Args:
            telegram_id: Telegram user ID.
            reason: Ban reason.
            until: Ban expiration.

        Returns:
            True if banned.
        """
        try:
            async with db_manager.session() as session:
                user = await user_repository.get_by_telegram_id(session, telegram_id)
                if user:
                    await user_repository.ban_user(session, user.id, reason, until)
                    logger.info(f"User {telegram_id} banned: {reason}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Ban error: {e}")
            return False

    async def get_user_stats(self, telegram_id: int) -> dict[str, Any]:
        """Get user statistics.

        Args:
            telegram_id: Telegram user ID.

        Returns:
            Statistics dictionary.
        """
        try:
            from app.repositories import ai_history_repository

            async with db_manager.session() as session:
                user = await user_repository.get_by_telegram_id(session, telegram_id)
                if not user:
                    return {}

                ai_stats = await ai_history_repository.get_user_stats(session, user.id)
                return {
                    "user_id": user.id,
                    "telegram_id": user.telegram_id,
                    "is_premium": user.is_premium,
                    "balance": user.balance,
                    "points": user.points,
                    "experience": user.experience,
                    "ai_usage": ai_stats,
                }
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {}


user_service = UserService()