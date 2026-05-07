# API Endpoints

Base URL: `/api/v1`

## Authentication

- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/refresh/`
- `POST /auth/logout/`
- `GET /auth/profile/`
- `POST /auth/password-reset/`
- `POST /auth/password-reset-confirm/`

## Activities

- `GET /activities/`
- `POST /activities/`
- `GET /activities/{id}/`

## Tasks

- `GET /tasks/`
- `POST /tasks/`
- `GET /tasks/{id}/`
- `PUT /tasks/{id}/`
- `PATCH /tasks/{id}/`
- `DELETE /tasks/{id}/`
- `POST /tasks/preview-ai/`
- `POST /tasks/{id}/complete/`

## Gamification

- `GET /gamification/summary/`
- `GET /gamification/transactions/`
- `GET /gamification/levels/`
- `GET /gamification/wallet/`
- `GET /gamification/streak/`

## Leaderboard

- `GET /leaderboard/all-time/`
- `GET /leaderboard/weekly/`
- `GET /leaderboard/me/`

## Reports

- `GET /reports/weekly/`
- `GET /reports/weekly-chart/`
- `GET /reports/category-breakdown/`

## Swagger / OpenAPI

- `GET /api/schema/`
- `GET /api/docs/`
