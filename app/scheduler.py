"""Scheduler entrypoint for periodic maintenance tasks."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.models import QARecord


async def run_scheduler() -> None:
    await init_db()
    while True:
        cutoff = datetime.now(timezone.utc) - timedelta(days=get_settings().retention_days)
        async with SessionLocal() as session:
            await session.execute(delete(QARecord).where(QARecord.created_at < cutoff))
            await session.commit()
        await asyncio.sleep(86400)


if __name__ == "__main__":
    asyncio.run(run_scheduler())
