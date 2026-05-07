# Questboard

Questboard is a full-stack university project: a gamified productivity app built with Django, Django REST Framework, React, Vite, Tailwind CSS, PostgreSQL, Redis, Celery, and Nginx.

The project lets a user:

- register and log in
- create and manage tasks
- get AI-assisted task classification with a safe local fallback
- earn XP, levels, streak progress, and rewards
- view leaderboard and weekly report screens

## Best Way To Review This Project

If you are opening this repository for grading or review, use the local review setup below. It is the simplest path and does not require an OpenAI key.

### Reviewer Quick Start

1. Clone the repository and open it in VS Code.
2. Copy `.env.example` to `.env`.
3. Start the backend:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_predefined_activities
   python manage.py runserver 0.0.0.0:8000
   ```

4. Start the frontend in a second terminal:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Open the app at [http://localhost:5173](http://localhost:5173).
6. Register a new account from the app and start using Questboard.

Notes:

- The default `.env.example` is configured for easy local review with SQLite.
- Real OpenAI classification is optional. If no OpenAI key is provided, the app falls back to local classification rules so task creation still works.
- Background jobs for reminders and scheduled streak logic are optional for review.

## Docker Review Option

If Docker Desktop is already installed, the full stack can also be started with Docker:

1. Copy `.env.example` to `.env`.
2. Run:

   ```bash
   docker compose up --build
   ```

3. Open:

- App: [http://localhost](http://localhost)
- API docs: [http://localhost/api/docs/](http://localhost/api/docs/)
- Django admin: [http://localhost/admin/](http://localhost/admin/)

Notes:

- The frontend talks to the backend through `/api/v1`, so the same app build works in both Docker and local development.
- PostgreSQL, Redis, Celery worker, and Celery Beat are included in the compose file for the full-stack version of the project.

## Project Structure

```text
backend/
  config/
  apps/
    users/
    activities/
    tasks/
    ai_engine/
    gamification/
    leaderboard/
    notifications/
    reports/
frontend/
  src/
docker/
  nginx/
scripts/
docs/
```

## Local Development Details

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_predefined_activities
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000`, so no extra frontend API setup is needed for the standard local workflow.

### Optional Services

Run these only if you want reminders or scheduled background processing:

```bash
cd backend
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

To use web push reminders, also add:

```env
VAPID_PUBLIC_KEY=your_public_key
VAPID_PRIVATE_KEY=your_private_key
VAPID_ADMIN_EMAIL=noreply@example.com
```

## Environment Notes

The repository includes `.env.example` but you should not publish your personal `.env` file.

Important variables:

- `DB_ENGINE=sqlite` keeps local review simple.
- `OPENAI_CLASSIFIER_ENABLED=0` keeps the project usable without an API key.
- `VITE_API_BASE_URL=/api/v1` works in both local dev and Docker.

If you want real OpenAI classification, set:

```env
OPENAI_API_KEY=your_key_here
OPENAI_CLASSIFIER_ENABLED=1
OPENAI_CLASSIFIER_MODEL=gpt-5-mini
```

## Testing

Backend tests:

```bash
cd backend
python manage.py test
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Architecture Overview

- Backend: modular Django apps with a service layer for AI classification, XP scoring, streak evaluation, level rewards, leaderboards, notifications, and reports.
- Frontend: React SPA with protected routes, token refresh handling, reusable dashboard components, and data charts.
- Infrastructure: Dockerized services for Django, PostgreSQL, Redis, Celery worker, Celery Beat, frontend static hosting, and Nginx reverse proxy.
- API: versioned under `/api/v1/` with Swagger docs at `/api/docs/`.

More detail lives in [docs/architecture.md](./docs/architecture.md), [docs/api.md](./docs/api.md), and [docs/ai-rules.md](./docs/ai-rules.md).

## Core Game Rules

- Task understanding can use a real OpenAI model when `OPENAI_API_KEY` and `OPENAI_CLASSIFIER_ENABLED=1` are set.
- If the OpenAI classifier is unavailable, the backend falls back to deterministic local rules so task creation still works.
- XP formula:

  ```text
  XP = round(completion_bonus + ((actual_duration_minutes / 3) * difficulty_multiplier))
  ```

- Difficulty multipliers:
  - easy = 1.0
  - medium = 2.0
  - hard = 3.5
  - extreme = 5.0
- Completion bonuses:
  - easy = 2
  - medium = 6
  - hard = 12
  - extreme = 20
- XP caps:
  - easy = 100
  - medium = 250
  - hard = 500
  - extreme = 800
- Level progression: every 500 XP increases level by 1.
- Rewards become claimable every 5 levels.

## Deployment Notes

- Frontend: deploy `frontend/` to Vercel with `VITE_API_BASE_URL` set to your backend URL plus `/api/v1`.
- Backend: deploy `backend/` to Railway or Render with:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=0`
  - `DATABASE_URL`
  - `DJANGO_ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`
  - `CSRF_TRUSTED_ORIGINS`
  - `FRONTEND_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_CLASSIFIER_ENABLED=1`

The backend supports `DATABASE_URL` for hosted PostgreSQL and serves Django static assets with WhiteNoise.
