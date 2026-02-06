# 100 Days of Making AI

A portfolio website documenting 100 days of building AI tools and projects. Each day, 1.5 hours is spent creating a self-contained AI project. This site showcases every project as a visual grid with individual blog posts.

## Stack

- **Python / Flask** — web framework
- **PostgreSQL** — database (Heroku), SQLite for local dev
- **Cloudinary** — image hosting and transformation
- **TinyMCE** — WYSIWYG editor for blog posts
- **Gunicorn** — production WSGI server

## Local Development

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # then edit with your values

# Initialize database and run
flask init-db
flask run
```

Visit `http://127.0.0.1:5000`. Admin panel at `/admin/login`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string. Defaults to `sqlite:///dev.db` locally. Auto-set by Heroku PostgreSQL add-on. |
| `CLOUDINARY_URL` | Cloudinary connection string (from your Cloudinary dashboard) |
| `ADMIN_PASSWORD` | Password for the admin panel |
| `SECRET_KEY` | Flask session secret key |

## Deploy to Heroku

```bash
# Install CLI and login
brew tap heroku/brew && brew install heroku
heroku login

# Create app with PostgreSQL
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0

# Set config vars
heroku config:set ADMIN_PASSWORD="your-secure-password"
heroku config:set SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
heroku config:set CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"

# Deploy
git push heroku main

# Initialize database
heroku run flask init-db
```

## Project Structure

```
├── app.py              # Flask app, routes, auth
├── models.py           # SQLAlchemy Project model
├── requirements.txt    # Python dependencies
├── Procfile            # Heroku process definition
├── runtime.txt         # Python version for Heroku
├── static/
│   └── style.css       # Responsive grid styles
└── templates/
    ├── base.html       # Shared layout
    ├── index.html      # Home page grid
    ├── project.html    # Project blog post
    ├── about.html      # About page
    ├── login.html      # Admin login
    └── admin/
        ├── dashboard.html  # Project management
        └── edit.html       # Create/edit with WYSIWYG
```

## Routes

**Public:** `/` (grid), `/project/<slug>` (blog post), `/about`

**Admin:** `/admin/login`, `/admin/dashboard`, `/admin/create`, `/admin/edit/<id>`, `/admin/delete/<id>`
