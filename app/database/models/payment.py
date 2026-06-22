"""Payment, Premium, Admin, Feedback, Notification, Settings models."""

from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, IDMixin, TimestampMixin
from app.database.enums import (
    FeedbackStatus, FeedbackType, NotificationType, PaymentMethod, PaymentStatus, SubscriptionPlan,
)


class PremiumPlan(Base, IDMixin, TimestampMixin):
    """Premium subscription plan definition."""

    __tablename__ = "premium_plans"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    plan_type: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, name="plan_type_enum"), nullable=False, index=True
    )
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="UZS", nullable=False)
    features: Mapped[list] = mapped_column(JSON, nullable=False)
    max_ai_requests_per_day: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_reminders: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    has_voice: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_ocr: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_priority_support: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<PremiumPlan(name={self.name}, price={self.price})>"


class PremiumUser(Base, IDMixin, TimestampMixin):
    """Active premium subscription of user."""

    __tablename__ = "premium_users"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("premium_plans.id", ondelete="RESTRICT"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<PremiumUser(user_id={self.user_id})>"


class Payment(Base, IDMixin, TimestampMixin):
    """Payment transaction record."""

    __tablename__ = "payments"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("premium_plans.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="UZS", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"), default=PaymentStatus.PENDING, nullable=False, index=True
    )
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum"), nullable=False
    )
    provider_payment_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    provider_charge_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    invoice_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Payment(user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class Transaction(Base, IDMixin, TimestampMixin):
    """Financial transaction log."""

    __tablename__ = "transactions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_before: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction(user_id={self.user_id}, amount={self.amount})>"


class Admin(Base, IDMixin, TimestampMixin):
    """Admin user with elevated privileges."""

    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    permissions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    appointed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    appointed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Admin(user_id={self.user_id}, level={self.level})>"


class AdminLog(Base, IDMixin, TimestampMixin):
    """Admin action audit log."""

    __tablename__ = "admin_logs"

    admin_id: Mapped[int] = mapped_column(
        ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<AdminLog(admin_id={self.admin_id}, action={self.action})>"


class Feedback(Base, IDMixin, TimestampMixin):
    """User feedback submission."""

    __tablename__ = "feedbacks"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    feedback_type: Mapped[FeedbackType] = mapped_column(
        Enum(FeedbackType, name="feedback_type_enum"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(256), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(FeedbackStatus, name="feedback_status_enum"),
        default=FeedbackStatus.NEW, nullable=False, index=True,
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attachments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    admin_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    responded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Feedback(user_id={self.user_id}, type={self.feedback_type})>"


class BugReport(Base, IDMixin, TimestampMixin):
    """Bug reports from users."""

    __tablename__ = "bug_reports"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    steps_to_reproduce: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="medium", nullable=False, index=True)
    environment: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False, index=True)
    attachments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    fixed_in_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    def __repr__(self) -> str:
        return f"<BugReport(user_id={self.user_id}, title={self.title})>"


class Notification(Base, IDMixin, TimestampMixin):
    """User notification."""

    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type_enum"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Notification(user_id={self.user_id}, type={self.notification_type})>"


class UserSetting(Base, IDMixin, TimestampMixin):
    """User-specific settings."""

    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marketing_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    health_tips: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weekly_report: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_start: Mapped[str | None] = mapped_column(String(8), nullable=True)
    quiet_hours_end: Mapped[str | None] = mapped_column(String(8), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(8), default="uz", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent", nullable=False)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<UserSetting(user_id={self.user_id})>"


class SystemSetting(Base, IDMixin, TimestampMixin):
    """Global system settings."""

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(32), default="string", nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<SystemSetting(key={self.key})>"


class Referral(Base, IDMixin, TimestampMixin):
    """User referral relationship."""

    __tablename__ = "referrals"

    referrer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    referred_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    referral_code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    bonus_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bonus_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Referral(referrer={self.referrer_id}, referred={self.referred_id})>"


class Achievement(Base, IDMixin, TimestampMixin):
    """User unlocked achievement."""

    __tablename__ = "achievements"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Achievement(user_id={self.user_id}, type={self.achievement_type})>"


class OCRHistory(Base, IDMixin, TimestampMixin):
    """OCR (image-to-text) processing history."""

    __tablename__ = "ocr_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    document_type: Mapped[str] = mapped_column(String(64), default="other", nullable=False, index=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="uz", nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<OCRHistory(user_id={self.user_id})>"


class VoiceHistory(Base, IDMixin, TimestampMixin):
    """Voice message transcription history."""

    __tablename__ = "voice_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    transcribed_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="uz", nullable=False)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<VoiceHistory(user_id={self.user_id})>"


class Statistics(Base, IDMixin, TimestampMixin):
    """Daily aggregated statistics."""

    __tablename__ = "statistics"

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), unique=True, nullable=False, index=True)
    new_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    premium_purchases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="UZS", nullable=False)

    def __repr__(self) -> str:
        return f"<Statistics(date={self.date})>"