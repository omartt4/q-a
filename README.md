# Q&A API

A FastAPI application that generates deterministic answers, records every submission in PostgreSQL, and caches answers in Redis for one hour.

## Architecture

The backend, PostgreSQL, Redis, worker, and scheduler run as Compose services on one private network. The backend connects to `postgres` and `redis` by service name; `localhost` would refer to the backend container itself. Only port `8000` is published.

Redis is an in-memory key/value store. The API checks Redis before generation, returns a cache hit immediately, and on a miss generates an answer, writes the Q&A row, then stores the answer with a TTL. Redis failures are logged and bypassed, so PostgreSQL and generation remain available. The scheduler removes records older than `RETENTION_DAYS` once per day.

Every request creates a history row, including cache hits. This keeps an auditable submission history while avoiding repeated answer generation.

## Run

Install [uv](https://docs.astral.sh/uv/), then run the API locally with:

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

The lockfile is committed, so `uv sync --locked` verifies reproducible dependencies.

For the complete PostgreSQL and Redis stack:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

PostgreSQL data is stored in the named `postgres_data` volume and survives container restarts.

## API

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/qa `
  -ContentType "application/json" -Body '{"question":"What is Redis?"}'
Invoke-RestMethod http://localhost:8000/qa/history
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod -Method Delete http://localhost:8000/qa/cache
```

## Database

`qa_records` uses a UUID primary key and stores the original question, answer, and timezone-aware `created_at`. The timestamp is indexed for history ordering. A single table is appropriate because each question has exactly one answer in this simple domain; separate tables would add joins and relationship-management overhead without representing a meaningful one-to-many relationship.

The SQL migration is in `migrations/001_initial.sql`. The application also creates the same schema on startup for a simple Compose deployment.

## Containers

The Dockerfile uses a build stage to install dependencies into a virtual environment and a runtime stage containing only Python, the environment, and application files. The runtime runs as non-root `appuser`. `EXPOSE` documents the container port; Compose `ports` performs host-to-container publishing.

## GitHub Actions and Docker Hub

Create Docker Hub repository `qa-backend`, then add either `DOCKERHUB_TOKEN` or `DOCKER_TOKEN` as a repository secret. Pushes to `main` run tests before the workflow logs in, builds with Buildx, and publishes `latest`, a commit-SHA tag, and release tags.

```powershell
docker pull YOUR_USERNAME/qa-backend:latest
docker run -p 8000:8000 `
  -e DATABASE_URL=postgresql+asyncpg://qa:password@host.docker.internal:5432/qa `
  -e REDIS_URL=redis://host.docker.internal:6379/0 `
  YOUR_USERNAME/qa-backend:latest
```

For normal operation, use Compose so service names and health checks are configured automatically.
