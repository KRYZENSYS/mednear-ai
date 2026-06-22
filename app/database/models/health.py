"""Health, Location, Appointments, Medical History models."""

from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, IDMixin, TimestampMixin
from app.database.enums import (
    AppointmentStatus, HealthMetricType, HospitalType, Severity,
)


class HealthMetric(Base, IDMixin, TimestampMixin):
    """Generic health metric tracking."""

    __tablename__ = "health_metrics"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_type: Mapped[HealthMetricType] = mapped_column(
        Enum(HealthMetricType, name="health_metric_type_enum"), nullable=False, index=True,
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    secondary_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<HealthMetric(user_id={self.user_id}, type={self.metric_type})>"


class BMIHistory(Base, IDMixin, TimestampMixin):
    """BMI calculation history."""

    __tablename__ = "bmi_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    bmi_value: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<BMIHistory(user_id={self.user_id}, bmi={self.bmi_value})>"


class BloodPressureHistory(Base, IDMixin, TimestampMixin):
    """Blood pressure readings."""

    __tablename__ = "blood_pressure_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    systolic: Mapped[int] = mapped_column(Integer, nullable=False)
    diastolic: Mapped[int] = mapped_column(Integer, nullable=False)
    pulse: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<BloodPressure(systolic={self.systolic}, diastolic={self.diastolic})>"


class BloodSugarHistory(Base, IDMixin, TimestampMixin):
    """Blood sugar readings."""

    __tablename__ = "blood_sugar_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    value_mmol: Mapped[float] = mapped_column(Float, nullable=False)
    measurement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<BloodSugar(value={self.value_mmol})>"


class Allergy(Base, IDMixin, TimestampMixin):
    """User allergies."""

    __tablename__ = "allergies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    allergen: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    reaction: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="allergy_severity_enum"), default=Severity.MODERATE, nullable=False
    )
    diagnosed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Allergy(user_id={self.user_id}, allergen={self.allergen})>"


class Vaccination(Base, IDMixin, TimestampMixin):
    """User vaccination history."""

    __tablename__ = "vaccinations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vaccine_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    dose_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    administered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    administered_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Vaccination(vaccine={self.vaccine_name})>"


class Prescription(Base, IDMixin, TimestampMixin):
    """Medical prescription records."""

    __tablename__ = "prescriptions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_name: Mapped[str] = mapped_column(String(256), nullable=False)
    clinic_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    medicines: Mapped[list] = mapped_column(JSON, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    def __repr__(self) -> str:
        return f"<Prescription(user_id={self.user_id}, diagnosis={self.diagnosis})>"


class Hospital(Base, IDMixin, TimestampMixin):
    """Hospital / Clinic / Pharmacy database."""

    __tablename__ = "hospitals"

    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    facility_type: Mapped[HospitalType] = mapped_column(
        Enum(HospitalType, name="facility_type_enum"), nullable=False, index=True
    )
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    city: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(64), default="Uzbekistan", nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    phone_numbers: Mapped[list | None] = mapped_column(JSON, nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    working_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    services: Mapped[list | None] = mapped_column(JSON, nullable=True)
    specializations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_24_7: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Hospital(name={self.name})>"


class Appointment(Base, IDMixin, TimestampMixin):
    """Medical appointment booking."""

    __tablename__ = "appointments"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hospital_id: Mapped[int | None] = mapped_column(
        ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True
    )
    doctor_name: Mapped[str] = mapped_column(String(256), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(128), nullable=True)
    appointment_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status_enum"),
        default=AppointmentStatus.SCHEDULED, nullable=False, index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Appointment(user_id={self.user_id}, doctor={self.doctor_name})>"


class EmergencyContact(Base, IDMixin, TimestampMixin):
    """User emergency contacts."""

    __tablename__ = "emergency_contacts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    relation: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<EmergencyContact(name={self.name})>"