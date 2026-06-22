"""Application-wide enum definitions.

Centralized enums for consistent values across database, services, and APIs.
"""

import enum


class UserRole(str, enum.Enum):
    """User role in the system."""

    USER = "user"
    PREMIUM = "premium"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, enum.Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Gender(str, enum.Enum):
    """User gender."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Language(str, enum.Enum):
    """Supported languages."""

    UZBEK = "uz"
    RUSSIAN = "ru"
    ENGLISH = "en"


class SubscriptionPlan(str, enum.Enum):
    """Premium subscription plans."""

    FREE = "free"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class PaymentStatus(str, enum.Enum):
    """Payment transaction status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Available payment methods."""

    CARD = "card"
    PAYME = "payme"
    CLICK = "click"
    UZUM = "uzum"
    TELEGRAM_STARS = "telegram_stars"


class ReminderType(str, enum.Enum):
    """Types of reminders."""

    MEDICINE = "medicine"
    WATER = "water"
    VITAMIN = "vitamin"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    MEAL = "meal"
    APPOINTMENT = "appointment"
    CUSTOM = "custom"


class ReminderFrequency(str, enum.Enum):
    """Reminder repeat frequency."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class HealthMetricType(str, enum.Enum):
    """Types of health metrics tracked."""

    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_SUGAR = "blood_sugar"
    HEART_RATE = "heart_rate"
    SLEEP_HOURS = "sleep_hours"
    WATER_INTAKE = "water_intake"
    STEPS = "steps"
    TEMPERATURE = "temperature"


class AppointmentStatus(str, enum.Enum):
    """Medical appointment status."""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class NotificationType(str, enum.Enum):
    """Notification categories."""

    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    PAYMENT = "payment"
    SYSTEM = "system"
    PROMOTION = "promotion"
    EMERGENCY = "emergency"
    FAMILY = "family"


class Severity(str, enum.Enum):
    """Medical severity levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class FeedbackType(str, enum.Enum):
    """User feedback categories."""

    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    QUESTION = "question"
    OTHER = "other"


class FeedbackStatus(str, enum.Enum):
    """Feedback processing status."""

    NEW = "new"
    IN_REVIEW = "in_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class HospitalType(str, enum.Enum):
    """Types of medical facilities."""

    HOSPITAL = "hospital"
    CLINIC = "clinic"
    PHARMACY = "pharmacy"
    LABORATORY = "laboratory"
    DENTAL = "dental"
    OPTICAL = "optical"
    REHABILITATION = "rehabilitation"
    EMERGENCY = "emergency"


class OCRType(str, enum.Enum):
    """OCR document types."""

    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    MEDICAL_REPORT = "medical_report"
    INVOICE = "invoice"
    CERTIFICATE = "certificate"
    OTHER = "other"


class AIProvider(str, enum.Enum):
    """AI service providers."""

    OPENAI_GPT = "openai_gpt"
    GOOGLE_GEMINI = "google_gemini"
    WHISPER = "whisper"
    GOOGLE_VISION = "google_vision"
    INTERNAL = "internal"


class AIRequestType(str, enum.Enum):
    """Types of AI requests."""

    CHAT = "chat"
    SYMPTOM_CHECK = "symptom_check"
    MEDICINE_ADVICE = "medicine_advice"
    NUTRITION = "nutrition"
    MENTAL_HEALTH = "mental_health"
    SKIN_ANALYSIS = "skin_analysis"
    PDF_ANALYSIS = "pdf_analysis"
    LAB_EXPLAIN = "lab_explain"
    VOICE_TRANSCRIPTION = "voice_transcription"
    TRANSLATION = "translation"


class AchievementType(str, enum.Enum):
    """User achievement types."""

    FIRST_CHAT = "first_chat"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    MEDICINE_STREAK = "medicine_streak"
    WATER_GOAL = "water_goal"
    PROFILE_COMPLETE = "profile_complete"
    FIRST_REMINDER = "first_reminder"
    HEALTH_TRACKER = "health_tracker"
    HUNDRED_DAYS = "hundred_days"
    REFERRAL_5 = "referral_5"
    REFERRAL_10 = "referral_10"


class BanReason(str, enum.Enum):
    """Reasons for user ban."""

    SPAM = "spam"
    ABUSE = "abuse"
    FRAUD = "fraud"
    VIOLATION = "violation"
    SECURITY = "security"
    USER_REQUEST = "user_request"
    INACTIVITY = "inactivity"


class DeviceType(str, enum.Enum):
    """User device types."""

    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"
    OTHER = "other"


class Theme(str, enum.Enum):
    """UI theme preference."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"