"""Chat, Medicine, Hospital, Appointment repositories."""

import math
from datetime import datetime
from typing import Sequence

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import (
    AIRequestType, AppointmentStatus, HospitalType, ReminderType,
)
from app.database.models.medical import (
    AIHistory, Chat, Disease, Medicine, MedicineReminder,
    Message, ReminderLog, Symptom,
)
from app.database.models.health import (
    Appointment, EmergencyContact, Hospital,
)
from app.repositories.base import BaseRepository
from app.utils.logger import logger


class ChatRepository(BaseRepository[Chat]):
    """Repository for Chat operations."""

    def __init__(self) -> None:
        """Initialize chat repository."""
        super().__init__(Chat)

    async def get_user_chats(
        self,
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        include_archived: bool = False,
    ) -> Sequence[Chat]:
        """Get user's chats.

        Args:
            session: Database session.
            user_id: User ID.
            skip: Pagination offset.
            limit: Pagination limit.
            include_archived: Include archived chats.

        Returns:
            List of user chats.
        """
        stmt = select(Chat).where(
            Chat.user_id == user_id,
            Chat.is_deleted == False,  # noqa: E712
        )
        if not include_archived:
            stmt = stmt.where(Chat.is_archived == False)  # noqa: E712
        stmt = stmt.order_by(desc(Chat.last_message_at)).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create_chat(
        self,
        session: AsyncSession,
        user_id: int,
        title: str,
        chat_type: str = "general",
    ) -> Chat:
        """Create a new chat session.

        Args:
            session: Database session.
            user_id: User ID.
            title: Chat title.
            chat_type: Type of chat.

        Returns:
            Created Chat instance.
        """
        chat = await self.create(
            session,
            user_id=user_id,
            title=title,
            chat_type=chat_type,
            last_message_at=datetime.utcnow(),
        )
        logger.info(f"Created chat id={chat.id} for user_id={user_id}")
        return chat

    async def archive_chat(
        self, session: AsyncSession, chat_id: int
    ) -> Chat | None:
        """Archive a chat.

        Args:
            session: Database session.
            chat_id: Chat ID.

        Returns:
            Updated chat or None.
        """
        return await self.update(session, chat_id, is_archived=True)

    async def touch_chat(
        self, session: AsyncSession, chat_id: int
    ) -> None:
        """Update last_message_at and increment message count.

        Args:
            session: Database session.
            chat_id: Chat ID.
        """
        chat = await self.get_by_id(session, chat_id)
        if chat:
            chat.last_message_at = datetime.utcnow()
            chat.message_count = (chat.message_count or 0) + 1
            await session.flush()


class MessageRepository(BaseRepository[Message]):
    """Repository for Message operations."""

    def __init__(self) -> None:
        """Initialize message repository."""
        super().__init__(Message)

    async def get_chat_messages(
        self,
        session: AsyncSession,
        chat_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Message]:
        """Get messages in chat.

        Args:
            session: Database session.
            chat_id: Chat ID.
            skip: Pagination offset.
            limit: Pagination limit.

        Returns:
            List of messages.
        """
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def add_message(
        self,
        session: AsyncSession,
        chat_id: int,
        user_id: int,
        role: str,
        content: str,
        tokens_used: int = 0,
        model: str | None = None,
        message_metadata: dict | None = None,
    ) -> Message:
        """Add new message to chat.

        Args:
            session: Database session.
            chat_id: Chat ID.
            user_id: User ID.
            role: Message role (user/assistant/system).
            content: Message content.
            tokens_used: Number of tokens used.
            model: AI model used.
            message_metadata: Additional metadata.

        Returns:
            Created Message instance.
        """
        message = await self.create(
            session,
            chat_id=chat_id,
            user_id=user_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            model=model,
            message_metadata=message_metadata,
        )
        return message


class AIHistoryRepository(BaseRepository[AIHistory]):
    """Repository for AI request history."""

    def __init__(self) -> None:
        """Initialize AI history repository."""
        super().__init__(AIHistory)

    async def log_request(
        self,
        session: AsyncSession,
        user_id: int,
        request_type: AIRequestType,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        duration_ms: int = 0,
        success: bool = True,
        error_message: str | None = None,
    ) -> AIHistory:
        """Log an AI request.

        Args:
            session: Database session.
            user_id: User ID.
            request_type: Type of AI request.
            provider: AI provider name.
            model: Model used.
            prompt: Input prompt.
            response: AI response.
            tokens_input: Input tokens.
            tokens_output: Output tokens.
            cost_usd: Cost in USD.
            duration_ms: Duration in milliseconds.
            success: Whether successful.
            error_message: Error message if failed.

        Returns:
            Created AIHistory instance.
        """
        from app.database.enums import AIProvider

        provider_enum = AIProvider(provider) if provider in AIProvider.__members__.values() else AIProvider.INTERNAL

        return await self.create(
            session,
            user_id=user_id,
            request_type=request_type,
            provider=provider_enum,
            model=model,
            prompt=prompt[:10000],
            response=response[:10000],
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )

    async def get_user_stats(
        self,
        session: AsyncSession,
        user_id: int,
        since: datetime | None = None,
    ) -> dict:
        """Get user AI usage statistics.

        Args:
            session: Database session.
            user_id: User ID.
            since: Start datetime.

        Returns:
            Statistics dictionary.
        """
        stmt = select(
            func.count(AIHistory.id).label("total_requests"),
            func.sum(AIHistory.tokens_input + AIHistory.tokens_output).label("total_tokens"),
            func.sum(AIHistory.cost_usd).label("total_cost"),
        ).where(AIHistory.user_id == user_id)

        if since:
            stmt = stmt.where(AIHistory.created_at >= since)

        result = await session.execute(stmt)
        row = result.one()
        return {
            "total_requests": row.total_requests or 0,
            "total_tokens": row.total_tokens or 0,
            "total_cost_usd": float(row.total_cost or 0),
        }


class MedicineRepository(BaseRepository[Medicine]):
    """Repository for Medicine catalog."""

    def __init__(self) -> None:
        """Initialize medicine repository."""
        super().__init__(Medicine)

    async def search_by_name(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> Sequence[Medicine]:
        """Search medicines by name.

        Args:
            session: Database session.
            query: Search query.
            limit: Result limit.

        Returns:
            Matching medicines.
        """
        search = f"%{query.lower()}%"
        stmt = (
            select(Medicine)
            .where(
                Medicine.is_active == True,  # noqa: E712
                or_(
                    func.lower(Medicine.name).like(search),
                    func.lower(Medicine.generic_name).like(search),
                ),
            )
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_atc_code(
        self, session: AsyncSession, atc_code: str
    ) -> Sequence[Medicine]:
        """Get medicines by ATC code.

        Args:
            session: Database session.
            atc_code: ATC classification code.

        Returns:
            Matching medicines.
        """
        stmt = select(Medicine).where(
            Medicine.atc_code == atc_code,
            Medicine.is_active == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalars().all()


class MedicineReminderRepository(BaseRepository[MedicineReminder]):
    """Repository for Medicine Reminder."""

    def __init__(self) -> None:
        """Initialize reminder repository."""
        super().__init__(MedicineReminder)

    async def get_user_reminders(
        self,
        session: AsyncSession,
        user_id: int,
        active_only: bool = True,
    ) -> Sequence[MedicineReminder]:
        """Get user's medicine reminders.

        Args:
            session: Database session.
            user_id: User ID.
            active_only: Return only active reminders.

        Returns:
            List of reminders.
        """
        stmt = select(MedicineReminder).where(
            MedicineReminder.user_id == user_id,
            MedicineReminder.is_deleted == False,  # noqa: E712
        )
        if active_only:
            stmt = stmt.where(MedicineReminder.is_active == True)  # noqa: E712
        stmt = stmt.order_by(MedicineReminder.next_reminder_at)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_due_reminders(
        self, session: AsyncSession, now: datetime | None = None
    ) -> Sequence[MedicineReminder]:
        """Get reminders due now.

        Args:
            session: Database session.
            now: Current datetime (default: now).

        Returns:
            Due reminders.
        """
        if now is None:
            now = datetime.utcnow()

        stmt = select(MedicineReminder).where(
            MedicineReminder.is_active == True,  # noqa: E712
            MedicineReminder.is_deleted == False,  # noqa: E712
            MedicineReminder.next_reminder_at <= now,
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_user_reminder_count(
        self, session: AsyncSession, user_id: int
    ) -> int:
        """Count active reminders for user.

        Args:
            session: Database session.
            user_id: User ID.

        Returns:
            Count.
        """
        return await self.count(session, user_id=user_id, is_active=True)


class HospitalRepository(BaseRepository[Hospital]):
    """Repository for Hospital / Clinic / Pharmacy."""

    def __init__(self) -> None:
        """Initialize hospital repository."""
        super().__init__(Hospital)

    async def search_nearby(
        self,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        facility_type: HospitalType | None = None,
        limit: int = 20,
    ) -> Sequence[Hospital]:
        """Search hospitals by location.

        Args:
            session: Database session.
            latitude: User latitude.
            longitude: User longitude.
            radius_km: Search radius in km.
            facility_type: Filter by type.
            limit: Result limit.

        Returns:
            List of nearby hospitals.
        """
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * max(math.cos(math.radians(latitude)), 0.01))

        stmt = select(Hospital).where(
            Hospital.is_active == True,  # noqa: E712
            Hospital.latitude.between(latitude - lat_range, latitude + lat_range),
            Hospital.longitude.between(longitude - lon_range, longitude + lon_range),
        )
        if facility_type:
            stmt = stmt.where(Hospital.facility_type == facility_type)

        stmt = stmt.order_by(desc(Hospital.rating)).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def search_by_city(
        self,
        session: AsyncSession,
        city: str,
        facility_type: HospitalType | None = None,
        limit: int = 50,
    ) -> Sequence[Hospital]:
        """Search hospitals by city.

        Args:
            session: Database session.
            city: City name.
            facility_type: Filter by type.
            limit: Result limit.

        Returns:
            Matching hospitals.
        """
        search = f"%{city}%"
        stmt = select(Hospital).where(
            Hospital.is_active == True,  # noqa: E712
            func.lower(Hospital.city).like(search.lower()),
        )
        if facility_type:
            stmt = stmt.where(Hospital.facility_type == facility_type)
        stmt = stmt.order_by(desc(Hospital.rating)).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()


class AppointmentRepository(BaseRepository[Appointment]):
    """Repository for medical appointments."""

    def __init__(self) -> None:
        """Initialize appointment repository."""
        super().__init__(Appointment)

    async def get_user_appointments(
        self,
        session: AsyncSession,
        user_id: int,
        upcoming_only: bool = False,
    ) -> Sequence[Appointment]:
        """Get user appointments.

        Args:
            session: Database session.
            user_id: User ID.
            upcoming_only: Only future appointments.

        Returns:
            List of appointments.
        """
        stmt = select(Appointment).where(
            Appointment.user_id == user_id,
            Appointment.is_deleted == False,  # noqa: E712
        )
        if upcoming_only:
            stmt = stmt.where(
                Appointment.appointment_at >= datetime.utcnow(),
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED
                ]),
            )
        stmt = stmt.order_by(Appointment.appointment_at)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_reminders(
        self, session: AsyncSession, hours: int = 24
    ) -> Sequence[Appointment]:
        """Get appointments needing reminder.

        Args:
            session: Database session.
            hours: Hours ahead to look.

        Returns:
            Appointments needing reminder.
        """
        from datetime import timedelta

        now = datetime.utcnow()
        until = now + timedelta(hours=hours)
        stmt = select(Appointment).where(
            Appointment.appointment_at.between(now, until),
            Appointment.reminder_sent == False,  # noqa: E712
            Appointment.status.in_([
                AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED
            ]),
        )
        result = await session.execute(stmt)
        return result.scalars().all()


class SymptomRepository(BaseRepository[Symptom]):
    """Repository for user symptoms."""

    def __init__(self) -> None:
        """Initialize symptom repository."""
        super().__init__(Symptom)

    async def get_user_recent_symptoms(
        self,
        session: AsyncSession,
        user_id: int,
        days: int = 30,
        limit: int = 50,
    ) -> Sequence[Symptom]:
        """Get user's recent symptoms.

        Args:
            session: Database session.
            user_id: User ID.
            days: Days to look back.
            limit: Max results.

        Returns:
            Recent symptoms.
        """
        from datetime import timedelta

        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Symptom)
            .where(
                Symptom.user_id == user_id,
                Symptom.is_deleted == False,  # noqa: E712
                Symptom.created_at >= since,
            )
            .order_by(desc(Symptom.created_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


class DiseaseRepository(BaseRepository[Disease]):
    """Repository for disease records."""

    def __init__(self) -> None:
        """Initialize disease repository."""
        super().__init__(Disease)

    async def get_user_active_diseases(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Disease]:
        """Get user's active diseases.

        Args:
            session: Database session.
            user_id: User ID.

        Returns:
            Active diseases.
        """
        stmt = select(Disease).where(
            Disease.user_id == user_id,
            Disease.is_active == True,  # noqa: E712
            Disease.is_deleted == False,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalars().all()


chat_repository = ChatRepository()
message_repository = MessageRepository()
ai_history_repository = AIHistoryRepository()
medicine_repository = MedicineRepository()
medicine_reminder_repository = MedicineReminderRepository()
hospital_repository = HospitalRepository()
appointment_repository = AppointmentRepository()
symptom_repository = SymptomRepository()
disease_repository = DiseaseRepository()