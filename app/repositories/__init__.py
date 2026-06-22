"""Repository layer - data access abstraction."""

from app.repositories.base import BaseRepository
from app.repositories.user import user_repository, UserRepository
from app.repositories.medical import (
    chat_repository, ChatRepository,
    message_repository, MessageRepository,
    ai_history_repository, AIHistoryRepository,
    medicine_repository, MedicineRepository,
    medicine_reminder_repository, MedicineReminderRepository,
    hospital_repository, HospitalRepository,
    appointment_repository, AppointmentRepository,
    symptom_repository, SymptomRepository,
    disease_repository, DiseaseRepository,
)

__all__ = [
    "BaseRepository",
    "user_repository", "UserRepository",
    "chat_repository", "ChatRepository",
    "message_repository", "MessageRepository",
    "ai_history_repository", "AIHistoryRepository",
    "medicine_repository", "MedicineRepository",
    "medicine_reminder_repository", "MedicineReminderRepository",
    "hospital_repository", "HospitalRepository",
    "appointment_repository", "AppointmentRepository",
    "symptom_repository", "SymptomRepository",
    "disease_repository", "DiseaseRepository",
]