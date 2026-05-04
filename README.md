# Blog Project

Professional Django blog API — small enterprise-style project for learning and demonstration.

## Purpose
- Learn Django and Django REST Framework by building a real-world blog backend.
- Demonstrate patterns used in production: modular apps, cursor pagination, token rotation/blacklist, rich-text editing with sanitization, and engagement features.

## Tech stack
- Python 3.11+
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (with refresh rotation + token blacklist)
- PostgreSQL (Docker)
- Redis (optional for OTP/session features)
- django-ckeditor (admin rich-text editing), server-side sanitization with `bleach`
- Docker & Docker Compose

## Features implemented
- Custom `accounts` app with JWT auth, refresh rotation and blacklisting.
- `blogs` app: Post and Category models, CRUD APIs, slug handling, CKEditor admin integration, server-side HTML sanitization.
- Cursor pagination for list endpoints (fast, scalable pagination).
- `engagement` app: Comments, Likes, Bookmarks with toggle endpoints.
- Defensive data migrations and tests for core APIs.

## Quick start (development)

Prerequisites:
- Git
- Docker & Docker Compose
- (Optional) Python 3.11 and pip if you prefer running locally without Docker

1. Clone the repository

```bash
git clone <repo-url> blog
cd blog
```

2. Copy env example

```bash
cp .env.example .env
# Edit .env to set secrets and DB credentials
```

3. Build and start services with Docker Compose

```bash
docker-compose up --build -d
```

4. Apply migrations

```bash
docker-compose exec backend python manage.py migrate
```

5. Create a superuser (for admin access)

```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Run tests

```bash
docker-compose exec backend python manage.py test
```

7. Access the app

- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/

## Running locally without Docker

1. Create virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (see `.env.example`) and run migrations

```bash
python manage.py migrate
python manage.py runserver
```

## Notes & recommendations
- The project includes `django-ckeditor` for admin rich-text editing. The package bundles CKEditor 4 which has known security advisories; consider migrating to CKEditor 5 or a different editor for production.
- Server-side sanitization is performed with `bleach` to ensure stored HTML is safe for rendering.
- The codebase uses refresh token rotation with blacklist support; ensure `token_blacklist` is enabled in production settings if you use token rotation.
- Sensitive values must be kept out of the repo — use `.env` and add secrets to your environment or a secrets manager. See `.env.example`.

## What to implement next (suggestions)
- Add CI that runs `python manage.py test` on pull requests.
- Harden settings for production (HTTPS, HSTS, secure cookies, allowed hosts, etc.).
- Add more API tests (permissions, update/delete flows, sanitization edge-cases).

## Contributing
Feel free to open issues or PRs. Follow standard git flow: create a branch, add tests for new behavior, and open a PR with a clear description.

---
Generated README by repository maintainer tooling.
