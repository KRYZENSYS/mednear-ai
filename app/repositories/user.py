"""User repository with user-specific operations."""

from datetime import datetime
from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import UserRole, UserStatus
from app.database.models.user import LoginHistory, Profile, User
from app.repositories.base import BaseRepository
from app.utils.logger import logger


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self) -> None:
        """Initialize user repository."""
        super().__init__(User)

    async def get_by_telegram_id(
        self, session: AsyncSession, telegram_id: int
    ) -> User | None:
        """Get user by Telegram ID.

        Args:
            session: Database session.
            telegram_id: Telegram user ID.

        Returns:
            User instance or None.
        """
        try:
            stmt = (
                select(User)
                .where(User.telegram_id == telegram_id)
                .where(User.is_deleted == False)  # noqa: E712
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            raise

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> User | None:
        """Get user by username.

        Args:
            session: Database session.
            username: Telegram username (without @).

        Returns:
            User instance or None.
        """
        username = username.lstrip("@").lower()
        stmt = select(User).where(
            func.lower(User.username) == username,
            User.is_deleted == False,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_referral_code(
        self, session: AsyncSession, code: str
    ) -> User | None:
        """Get user by referral code.

        Args:
            session: Database session.
            code: Referral code.

        Returns:
            User instance or None.
        """
        stmt = select(User).where(User.referral_code == code.upper())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        language_code: str = "uz",
        referral_code: str | None = None,
    ) -> User:
        """Create a new user with default settings.

        Args:
            session: Database session.
            telegram_id: Telegram user ID.
            first_name: User first name.
            last_name: User last name.
            username: Telegram username.
            language_code: Telegram language code.
            referral_code: Referral code used during registration.

        Returns:
            Created User instance.
        """
        from app.utils.helpers import generate_referral_code

        referred_by_id = None
        if referral_code:
            referrer = await self.get_by_referral_code(session, referral_code)
            if referrer:
                referred_by_id = referrer.id

        new_code = generate_referral_code()
        while await self.get_by_referral_code(session, new_code):
            new_code = generate_referral_code()

        lang_map = {"uz": "uz", "ru": "ru", "en": "en"}
        language = lang_map.get(language_code, "uz")

        user = await self.create(
            session,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language=language,
            referral_code=new_code,
            referred_by_id=referred_by_id,
            last_activity_at=datetime.utcnow(),
        )

        await self.create_profile(session, user.id)
        logger.info(f"Created new user telegram_id={telegram_id}, id={user.id}")
        return user

    async def create_profile(
        self, session: AsyncSession, user_id: int
    ) -> Profile:
        """Create empty profile for user.

        Args:
            session: Database session.
            user_id: User ID.

        Returns:
            Created Profile instance.
        """
        profile = Profile(user_id=user_id)
        session.add(profile)
        await session.flush()
        return profile

    async def get_or_create(
        self,
        session: AsyncSession,
        telegram_id: int,
        **kwargs: object,
    ) -> tuple[User, bool]:
        """Get existing user or create new one.

        Args:
            session: Database session.
            telegram_id: Telegram user ID.
            **kwargs: Additional fields for creation.

        Returns:
            Tuple of (User, created) where created is True if new.
        """
        user = await self.get_by_telegram_id(session, telegram_id)
        if user:
            user.last_activity_at = datetime.utcnow()
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            await session.flush()
            return user, False

        user = await self.create_user(session, telegram_id=telegram_id, **kwargs)
        return user, True

    async def update_activity(
        self, session: AsyncSession, user_id: int
    ) -> None:
        """Update user last activity timestamp.

        Args:
            session: Database session.
            user_id: User ID.
        """
        await self.update(session, user_id, last_activity_at=datetime.utcnow())

    async def ban_user(
        self,
        session: AsyncSession,
        user_id: int,
        reason: str,
        until: datetime | None = None,
    ) -> User | None:
        """Ban a user.

        Args:
            session: Database session.
            user_id: User ID.
            reason: Ban reason.
            until: Ban expiration (None = permanent).

        Returns:
            Updated user or None.
        """
        return await self.update(
            session,
            user_id,
            status=UserStatus.BANNED,
            ban_reason=reason,
            banned_until=until,
        )

    async def unban_user(
        self, session: AsyncSession, user_id: int
    ) -> User | None:
        """Unban a user.

        Args:
            session: Database session.
            user_id: User ID.

        Returns:
            Updated user or None.
        """
        return await self.update(
            session,
            user_id,
            status=UserStatus.ACTIVE,
            ban_reason=None,
            banned_until=None,
        )

    async def activate_premium(
        self,
        session: AsyncSession,
        user_id: int,
        until: datetime,
    ) -> User | None:
        """Activate premium subscription.

        Args:
            session: Database session.
            user_id: User ID.
            until: Premium expiration datetime.

        Returns:
            Updated user or None.
        """
        return await self.update(
            session,
            user_id,
            is_premium=True,
            premium_until=until,
        )

    async def get_admins(
        self, session: AsyncSession
    ) -> Sequence[User]:
        """Get all admin users.

        Args:
            session: Database session.

        Returns:
            List of admin users.
        """
        stmt = select(User).where(
            User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN]),
            User.status == UserStatus.ACTIVE,
            User.is_deleted == False,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def search_users(
        self,
        session: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[User]:
        """Search users by name or username.

        Args:
            session: Database session.
            query: Search query.
            skip: Pagination skip.
            limit: Pagination limit.

        Returns:
            Matching users.
        """
        search = f"%{query.lower()}%"
        stmt = select(User).where(
            User.is_deleted == False,  # noqa: E712
            or_(
                func.lower(User.first_name).like(search),
                func.lower(User.last_name).like(search),
                func.lower(User.username).like(search),
            ),
        ).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_active_users_count(
        self, session: AsyncSession, since: datetime | None = None
    ) -> int:
        """Get count of active users.

        Args:
            session: Database session.
            since: Activity since datetime (default: last 24h).

        Returns:
            Number of active users.
        """
        from datetime import timedelta

        if since is None:
            since = datetime.utcnow() - timedelta(days=1)

        stmt = select(func.count(User.id)).where(
            User.last_activity_at >= since,
            User.status == UserStatus.ACTIVE,
            User.is_deleted == False,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalar_one() or 0

    async def add_login_history(
        self,
        session: AsyncSession,
        user_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None,
        success: bool = True,
        failure_reason: str | None = None,
    ) -> LoginHistory:
        """Record a login attempt.

        Args:
            session: Database session.
            user_id: User ID.
            ip_address: IP address.
            user_agent: User agent string.
            success: Whether login was successful.
            failure_reason: Reason if failed.

        Returns:
            Created LoginHistory record.
        """
        history = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
        )
        session.add(history)
        await session.flush()
        return history


user_repository = UserRepository()