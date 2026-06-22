"""Medical-related database models: Chat, AI History, Symptoms, Diseases, Medicines."""

from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, IDMixin, TimestampMixin
from app.database.enums import AIProvider, AIRequestType, Severity


class Chat(Base, IDMixin, TimestampMixin):
    """Chat session between user and AI."""

    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    chat_type: Mapped[str] = mapped_column(String(64), default="general", nullable=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    messages = relationship(
        "Message", back_populates="chat",
        cascade="all, delete-orphan", order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base, IDMixin, TimestampMixin):
    """Individual message in a chat."""

    __tablename__ = "messages"

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    chat = relationship("Chat", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, role={self.role})>"


class AIHistory(Base, IDMixin, TimestampMixin):
    """AI request history for analytics and billing."""

    __tablename__ = "ai_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    request_type: Mapped[AIRequestType] = mapped_column(
        Enum(AIRequestType, name="ai_request_type_enum"), nullable=False, index=True
    )
    provider: Mapped[AIProvider] = mapped_column(
        Enum(AIProvider, name="ai_provider_enum"), nullable=False
    )
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AIHistory(user_id={self.user_id}, type={self.request_type})>"


class Symptom(Base, IDMixin, TimestampMixin):
    """User reported symptoms."""

    __tablename__ = "symptoms"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="symptom_severity_enum"),
        default=Severity.LOW, nullable=False, index=True,
    )
    body_part: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_chronic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Symptom(user_id={self.user_id}, name={self.name})>"


class Disease(Base, IDMixin, TimestampMixin):
    """Disease/diagnosis information."""

    __tablename__ = "diseases"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    icd_code: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="disease_severity_enum"),
        default=Severity.MODERATE, nullable=False,
    )
    diagnosed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    diagnosed_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_chronic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    treatment: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Disease(user_id={self.user_id}, name={self.name})>"


class Medicine(Base, IDMixin, TimestampMixin):
    """Medicine database (global catalog)."""

    __tablename__ = "medicines"

    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    generic_name: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    brand_names: Mapped[list | None] = mapped_column(JSON, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(256), nullable=True)
    atc_code: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    dosage_form: Mapped[str | None] = mapped_column(String(64), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    indications: Mapped[str | None] = mapped_column(Text, nullable=True)
    contraindications: Mapped[str | None] = mapped_column(Text, nullable=True)
    side_effects: Mapped[str | None] = mapped_column(Text, nullable=True)
    dosage_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    interactions: Mapped[str | None] = mapped_column(Text, nullable=True)
    pregnancy_safe: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_prescription: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    average_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="UZS", nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Medicine(name={self.name})>"


class MedicineReminder(Base, IDMixin, TimestampMixin):
    """User-specific medicine reminder."""

    __tablename__ = "medicine_reminders"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medicine_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicines.id", ondelete="SET NULL"), nullable=True
    )
    custom_medicine_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    dosage: Mapped[str] = mapped_column(String(64), nullable=False)
    frequency: Mapped[str] = mapped_column(String(32), default="daily", nullable=False)
    times: Mapped[list] = mapped_column(JSON, nullable=False)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    with_food: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<MedicineReminder(user_id={self.user_id})>"


class ReminderLog(Base, IDMixin, TimestampMixin):
    """Log of reminder firings and user responses."""

    __tablename__ = "reminder_logs"

    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("medicine_reminders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    skipped_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)

    def __repr__(self) -> str:
        return f"<ReminderLog(reminder_id={self.reminder_id}, status={self.status})>"