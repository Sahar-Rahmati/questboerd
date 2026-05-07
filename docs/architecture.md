# Architecture Overview

## Backend

### App Boundaries

- `users`: registration, JWT login/logout, refresh, password reset, user profile.
- `activities`: predefined activity bank and custom activity creation.
- `tasks`: task lifecycle, AI preview, AI-enriched creation, task completion.
- `ai_engine`: deterministic keyword and numeric parsing classifier plus XP estimation helpers.
- `gamification`: XP transactions, level history, wallet rewards, streak logs, reward orchestration.
- `leaderboard`: all-time and weekly ranking services with cache-backed responses.
- `reports`: weekly analytics aggregates for cards, charts, and hardest-task summaries.

### Design Rules

- Thin API views.
- Serializer-based validation.
- Service-layer orchestration for domain logic.
- Server-side only scoring, reward, and level decisions.
- UUID primary keys for domain models.
- Query optimization through `select_related`, aggregation, ordering, and cache usage.
- Environment-driven configuration for secrets and infrastructure endpoints.

## Frontend

- React SPA with React Router protected routes.
- Axios request and response interceptors for auth headers and refresh flow.
- Reusable card, chart, task, and layout components.
- Responsive Tailwind UI with dashboard-style pages for tasks, reports, leaderboard, wallet, and profile.

## Infrastructure

- PostgreSQL for persistent relational data.
- Redis for cache and Celery broker/result backend.
- Celery worker for async jobs.
- Celery Beat for nightly streak evaluation.
- Nginx for reverse proxying the React frontend and Django API.

## Data Flow

1. User previews a task.
2. Frontend calls `POST /api/v1/tasks/preview-ai/`.
3. `ai_engine.services.classify_task` returns category, difficulty, duration, multiplier, and explanation.
4. On task creation, the same rule-based classification is persisted on the task.
5. On completion, the backend calculates XP, applies anomaly rules and XP caps, writes task completion and XP transaction records, updates level, awards wallet milestones if eligible, and returns the XP breakdown.
6. Nightly streak evaluation grants streak bonuses through the same XP transaction pipeline.
