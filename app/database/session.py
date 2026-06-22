"""Async database engine and session management.

Provides SQLAlchemy async engine with connection pooling
and dependency-injection-friendly session factory.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.database.base import Base
from app.utils.logger import logger


class DatabaseManager:
    """Manages database connections and sessions.

    Implements singleton pattern for engine and session factory.
    """

    _instance: "DatabaseManager | None" = None
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    def __new__(cls) -> "DatabaseManager":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize()
        return cls._instance

    @classmethod
    def _initialize(cls) -> None:
        """Initialize engine and session factory."""
        try:
            cls._engine = create_async_engine(
                settings.db.async_url,
                echo=settings.db.echo,
                pool_size=settings.db.pool_size,
                max_overflow=settings.db.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                future=True,
            )

            cls._session_factory = async_sessionmaker(
                bind=cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            logger.info(
                f"Database initialized | Host: {settings.db.host} | "
                f"DB: {settings.db.name} | Pool: {settings.db.pool_size}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    @property
    def engine(self) -> AsyncEngine:
        """Get database engine."""
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get session factory."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session context manager.

        Yields:
            AsyncSession: Database session with automatic cleanup.

        Example:
            >>> async with db.session() as session:
            ...     result = await session.execute(select(User))
        """
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()

    async def create_all(self) -> None:
        """Create all tables defined in Base metadata."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All database tables created")

    async def drop_all(self) -> None:
        """Drop all tables. USE WITH CAUTION - only for testing."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")

    async def close(self) -> None:
        """Close database engine and cleanup connections."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")


db_manager = DatabaseManager()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session.

    Yields:
        AsyncSession: Database session.
    """
    async with db_manager.session() as session:
        yield session