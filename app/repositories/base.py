"""Base repository pattern implementation.

Provides generic CRUD operations for all repositories.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base, SoftDeleteMixin
from app.utils.logger import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """Generic base repository with common CRUD operations.

    Type Parameters:
        ModelType: SQLAlchemy model class.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """Initialize repository with model class.

        Args:
            model: SQLAlchemy model class.
        """
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> ModelType | None:
        """Get record by primary key.

        Args:
            session: Database session.
            id: Primary key value.

        Returns:
            Model instance or None.
        """
        try:
            stmt = select(self.model).where(self.model.id == id)
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error in get_by_id({self.model.__name__}, {id}): {e}")
            raise

    async def get_all(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> Sequence[ModelType]:
        """Get all records with pagination.

        Args:
            session: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records.
            order_by: Field name to order by.
            descending: Sort in descending order.

        Returns:
            List of model instances.
        """
        try:
            stmt = select(self.model)
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
            if order_by and hasattr(self.model, order_by):
                column = getattr(self.model, order_by)
                stmt = stmt.order_by(column.desc() if descending else column.asc())
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error in get_all({self.model.__name__}): {e}")
            raise

    async def create(self, session: AsyncSession, **kwargs: Any) -> ModelType:
        """Create new record.

        Args:
            session: Database session.
            **kwargs: Model fields.

        Returns:
            Created model instance.
        """
        try:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            logger.debug(f"Created {self.model.__name__} with id={instance.id}")
            return instance
        except Exception as e:
            logger.error(f"Error in create({self.model.__name__}): {e}")
            raise

    async def update(
        self, session: AsyncSession, id: int, **kwargs: Any
    ) -> ModelType | None:
        """Update record by ID.

        Args:
            session: Database session.
            id: Primary key.
            **kwargs: Fields to update.

        Returns:
            Updated instance or None.
        """
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**kwargs)
                .returning(self.model)
            )
            result = await session.execute(stmt)
            updated = result.scalar_one_or_none()
            if updated:
                await session.flush()
                await session.refresh(updated)
                logger.debug(f"Updated {self.model.__name__} id={id}")
            return updated
        except Exception as e:
            logger.error(f"Error in update({self.model.__name__}, {id}): {e}")
            raise

    async def delete(self, session: AsyncSession, id: int, hard: bool = False) -> bool:
        """Delete record by ID.

        Args:
            session: Database session.
            id: Primary key.
            hard: If True, actually delete; if False, soft delete.

        Returns:
            True if deleted, False if not found.
        """
        try:
            if hard or not hasattr(self.model, "is_deleted"):
                stmt = delete(self.model).where(self.model.id == id)
                await session.execute(stmt)
            else:
                stmt = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(is_deleted=True, deleted_at=datetime.utcnow())
                )
                await session.execute(stmt)
            logger.debug(f"Deleted {self.model.__name__} id={id} (hard={hard})")
            return True
        except Exception as e:
            logger.error(f"Error in delete({self.model.__name__}, {id}): {e}")
            raise

    async def count(self, session: AsyncSession, **filters: Any) -> int:
        """Count records matching filters.

        Args:
            session: Database session.
            **filters: Field=value filters.

        Returns:
            Number of matching records.
        """
        try:
            stmt = select(func.count(self.model.id))
            if filters:
                conditions = [
                    getattr(self.model, key) == value for key, value in filters.items()
                    if hasattr(self.model, key)
                ]
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
            result = await session.execute(stmt)
            return result.scalar_one() or 0
        except Exception as e:
            logger.error(f"Error in count({self.model.__name__}): {e}")
            raise

    async def exists(self, session: AsyncSession, id: int) -> bool:
        """Check if record exists.

        Args:
            session: Database session.
            id: Primary key.

        Returns:
            True if exists.
        """
        count = await self.count(session, id=id)
        return count > 0

    async def filter_by(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
        **filters: Any,
    ) -> Sequence[ModelType]:
        """Filter records by given criteria.

        Args:
            session: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records.
            order_by: Field to order by.
            descending: Sort descending.
            **filters: Field=value filters.

        Returns:
            List of matching records.
        """
        try:
            stmt = select(self.model)
            if filters:
                conditions = [
                    getattr(self.model, key) == value
                    for key, value in filters.items()
                    if hasattr(self.model, key)
                ]
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
            if order_by and hasattr(self.model, order_by):
                column = getattr(self.model, order_by)
                stmt = stmt.order_by(column.desc() if descending else column.asc())
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error in filter_by({self.model.__name__}): {e}")
            raise