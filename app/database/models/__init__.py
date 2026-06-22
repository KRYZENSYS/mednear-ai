"""Database models package.

Imports all SQLAlchemy models so they are registered with Base.metadata.
"""

from app.database.models.user import User, Profile, DeviceSession, LoginHistory
from app.database.models.medical import (
    Chat, Message, AIHistory, Symptom, Disease,
    Medicine, MedicineReminder, ReminderLog,
)
from app.database.models.health import (
    HealthMetric, BMIHistory, BloodPressureHistory, BloodSugarHistory,
    Allergy, Vaccination, Prescription, Hospital, Appointment, EmergencyContact,
)
from app.database.models.payment import (
    PremiumPlan, PremiumUser, Payment, Transaction,
    Admin, AdminLog, Feedback, BugReport,
    Notification, UserSetting, SystemSetting,
    Referral, Achievement, OCRHistory, VoiceHistory, Statistics,
)

__all__ = [
    # User models
    "User", "Profile", "DeviceSession", "LoginHistory",
    # Medical models
    "Chat", "Message", "AIHistory", "Symptom", "Disease",
    "Medicine", "MedicineReminder", "ReminderLog",
    # Health models
    "HealthMetric", "BMIHistory", "BloodPressureHistory", "BloodSugarHistory",
    "Allergy", "Vaccination", "Prescription", "Hospital", "Appointment", "EmergencyContact",
    # Payment & Admin models
    "PremiumPlan", "PremiumUser", "Payment", "Transaction",
    "Admin", "AdminLog", "Feedback", "BugReport",
    "Notification", "UserSetting", "SystemSetting",
    "Referral", "Achievement", "OCRHistory", "VoiceHistory", "Statistics",
]