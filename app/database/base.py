"""SQLAlchemy declarative base with common mixins."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.utils.helpers import generate_random_string


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides common functionality and table naming conventions.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-generate table name from class name (snake_case)."""
        import re
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        if not name.endswith("s"):
            name += "s"
        return name

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def __repr__(self) -> str:
        """String representation showing class name and ID."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


class TimestampMixin:
    """Mixin adding created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True,
    )


class SoftDeleteMixin:
    """Mixin adding soft delete functionality."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def soft_delete(self) -> None:
        """Mark record as soft deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()


class AuditMixin:
    """Mixin adding audit fields for tracking changes."""

    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)


class IDMixin:
    """Mixin adding primary key ID."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )