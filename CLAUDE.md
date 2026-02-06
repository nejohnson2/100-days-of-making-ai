# CLAUDE.md

## Project Overview

This is a Flask portfolio website for the "100 Days of Making AI" challenge. It displays a grid of project thumbnails that link to individual blog posts, with an admin backend for content management.

## Commands

- `flask run` — start local dev server (port 5000)
- `flask init-db` — create database tables
- `pip install -r requirements.txt` — install dependencies
- `git push heroku main` — deploy to Heroku
- `heroku run flask init-db` — initialize Heroku database

## Architecture

- **app.py** — single-file Flask app with all routes and configuration. Public routes serve the grid homepage, project detail pages, and about page. Admin routes (protected by `@login_required` decorator) handle CRUD for projects.
- **models.py** — one model: `Project` with fields: title, slug, day_number, image_url, content (HTML), created_at, updated_at. Uses `Project.make_slug()` for URL-safe slugs.
- **Authentication** — simple session-based password check against `ADMIN_PASSWORD` env var. No user model or registration.
- **Images** — uploaded to Cloudinary via Python SDK, auto-cropped to 800x800 square. Stored as URLs in the database.
- **Database** — SQLite locally (`sqlite:///dev.db`), PostgreSQL on Heroku. The `DATABASE_URL` env var controls this. Heroku's `postgres://` prefix is auto-converted to `postgresql://` for SQLAlchemy compatibility.
- **WYSIWYG** — TinyMCE 6 loaded from jsDelivr CDN (GPL license). Content stored as raw HTML.

## Key Patterns

- All admin routes use the `@login_required` decorator defined in app.py
- Templates extend `base.html` which provides nav, flash messages, and footer
- The home page grid uses CSS Grid with square aspect ratio cards (`padding-bottom: 100%`)
- Project content is rendered with `{{ project.content | safe }}` (trusted admin HTML)
- Slugs are auto-generated from titles; duplicates get `-day-N` appended

## Environment

Requires `.env` file locally with: `DATABASE_URL`, `CLOUDINARY_URL`, `ADMIN_PASSWORD`, `SECRET_KEY`. On Heroku, `DATABASE_URL` is set automatically by the PostgreSQL add-on.
