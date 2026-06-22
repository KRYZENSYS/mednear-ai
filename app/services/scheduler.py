"""Scheduler service for periodic tasks and reminders."""

from datetime import datetime
from typing import Any, Callable

from app.utils.logger import logger


class SchedulerService:
    """Async task scheduler using APScheduler.

    Handles periodic jobs like sending reminders, cleaning up data,
    generating statistics, etc.
    """

    def __init__(self) -> None:
        """Initialize scheduler service."""
        self._scheduler: Any = None
        self._started: bool = False

    async def start(self) -> None:
        """Start the scheduler."""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger

            self._scheduler = AsyncIOScheduler(timezone="UTC")

            self._scheduler.add_job(
                self._send_pending_reminders,
                CronTrigger(minute="*"),
                id="send_reminders",
                name="Send pending reminders",
                replace_existing=True,
            )

            self._scheduler.add_job(
                self._send_appointment_reminders,
                CronTrigger(minute="*/15"),
                id="appointment_reminders",
                name="Send appointment reminders",
                replace_existing=True,
            )

            self._scheduler.add_job(
                self._update_statistics,
                CronTrigger(hour=0, minute=5),
                id="daily_stats",
                name="Update daily statistics",
                replace_existing=True,
            )

            self._scheduler.add_job(
                self._cleanup_old_data,
                CronTrigger(hour=3, minute=0),
                id="cleanup",
                name="Cleanup old data",
                replace_existing=True,
            )

            self._scheduler.start()
            self._started = True
            logger.info(f"Scheduler started with {len(self._scheduler.get_jobs())} jobs")
        except ImportError:
            logger.warning("APScheduler not available, scheduler disabled")
        except Exception as e:
            logger.error(f"Scheduler start failed: {e}", exc_info=True)

    async def stop(self) -> None:
        """Stop the scheduler."""
        if self._scheduler and self._started:
            try:
                self._scheduler.shutdown(wait=False)
                self._started = False
                logger.info("Scheduler stopped")
            except Exception as e:
                logger.warning(f"Scheduler stop error: {e}")

    async def _send_pending_reminders(self) -> None:
        """Send pending medicine reminders."""
        from app.database import db_manager
        from app.repositories import medicine_reminder_repository

        try:
            async with db_manager.session() as session:
                reminders = await medicine_reminder_repository.get_due_reminders(session)
                logger.debug(f"Found {len(reminders)} due reminders")
                for reminder in reminders:
                    logger.debug(f"Would send reminder id={reminder.id}")
        except Exception as e:
            logger.error(f"Reminder job error: {e}", exc_info=True)

    async def _send_appointment_reminders(self) -> None:
        """Send appointment reminders."""
        from app.database import db_manager
        from app.repositories import appointment_repository

        try:
            async with db_manager.session() as session:
                appointments = await appointment_repository.get_upcoming_reminders(session, hours=24)
                logger.debug(f"Found {len(appointments)} appointments needing reminder")
        except Exception as e:
            logger.error(f"Appointment reminder job error: {e}", exc_info=True)

    async def _update_statistics(self) -> None:
        """Update daily statistics."""
        logger.debug("Updating daily statistics")
        try:
            from app.database import db_manager
            from sqlalchemy import select
            from app.database.models.payment import Statistics

            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            async with db_manager.session() as session:
                stmt = select(Statistics).where(Statistics.date == today)
                result = await session.execute(stmt)
                stat = result.scalar_one_or_none()
                if not stat:
                    session.add(Statistics(date=today))
                    await session.commit()
                    logger.info(f"Created statistics record for {today.date()}")
        except Exception as e:
            logger.error(f"Stats job error: {e}", exc_info=True)

    async def _cleanup_old_data(self) -> None:
        """Cleanup old data (logs, expired sessions, etc.)."""
        logger.debug("Running cleanup job")

    def add_job(
        self,
        func: Callable,
        trigger: str = "interval",
        **kwargs: Any,
    ) -> None:
        """Add custom job to scheduler.

        Args:
            func: Async function to execute.
            trigger: Trigger type (interval, cron, date).
            **kwargs: Trigger parameters.
        """
        if not self._scheduler:
            logger.warning("Scheduler not initialized")
            return
        try:
            self._scheduler.add_job(func, trigger, **kwargs)
            logger.debug(f"Added job: {func.__name__}")
        except Exception as e:
            logger.error(f"Failed to add job: {e}")


scheduler_service = SchedulerService()