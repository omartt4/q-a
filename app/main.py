from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_answer, clear_cache, get_cached_answer, redis_is_healthy
from app.config import get_settings
from app.db import engine, get_db, init_db
from app.models import QARecord
from app.schemas import HealthResponse, QAResponse, QuestionRequest
from app.services import generate_answer


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", redis="ok" if await redis_is_healthy() else "unavailable")


@app.post("/qa", response_model=QAResponse, status_code=status.HTTP_201_CREATED)
async def ask_question(payload: QuestionRequest, db: AsyncSession = Depends(get_db)) -> QAResponse:
    cached_answer = await get_cached_answer(payload.question)
    answer = cached_answer if cached_answer is not None else generate_answer(payload.question)
    record = QARecord(question=payload.question, answer=answer)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    if cached_answer is None:
        await cache_answer(payload.question, answer)
    return QAResponse.model_validate({**record.__dict__, "cached": cached_answer is not None})


@app.get("/qa/history", response_model=list[QAResponse])
async def history(
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[QAResponse]:
    result = await db.execute(select(QARecord).order_by(desc(QARecord.created_at)).limit(limit))
    return [QAResponse.model_validate({**record.__dict__, "cached": False}) for record in result.scalars()]


@app.delete("/qa/cache", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cache() -> None:
    await clear_cache()


@app.get("/qa/{record_id}", response_model=QAResponse)
async def get_record(record_id: UUID, db: AsyncSession = Depends(get_db)) -> QAResponse:
    result = await db.execute(select(QARecord).where(QARecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Q&A record not found")
    return QAResponse.model_validate({**record.__dict__, "cached": False})
