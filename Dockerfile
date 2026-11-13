FROM python:3.12-slim AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /build
RUN pip install --no-cache-dir uv==0.9.4
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY migrations ./migrations
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --system appuser && useradd --system --gid appuser --create-home appuser
WORKDIR /app
COPY --from=build --chown=appuser:appuser /build/.venv ./.venv
COPY --from=build --chown=appuser:appuser /build/app ./app
COPY --from=build --chown=appuser:appuser /build/migrations ./migrations
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
