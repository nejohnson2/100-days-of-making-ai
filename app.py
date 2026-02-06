import os
from functools import wraps

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import Project, db

load_dotenv()

app = Flask(__name__)

# Config
database_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
# Heroku uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

# Cloudinary config
cloudinary.config(secure=True)

# Initialize database
db.init_app(app)


# --- Auth ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid password.", "error")
    return render_template("login.html")


@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))


# --- Public Routes ---
@app.route("/")
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("index.html", projects=projects)


@app.route("/project/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template("project.html", project=project)


@app.route("/about")
def about():
    return render_template("about.html")


# --- Admin Routes ---
@app.route("/admin")
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    projects = Project.query.order_by(Project.day_number.desc()).all()
    return render_template("admin/dashboard.html", projects=projects)


@app.route("/admin/create", methods=["GET", "POST"])
@login_required
def admin_create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        day_number = request.form.get("day_number", type=int)
        content = request.form.get("content", "")
        image = request.files.get("image")

        if not title or not day_number:
            flash("Title and day number are required.", "error")
            return render_template("admin/edit.html", project=None)

        # Upload image to Cloudinary
        image_url = ""
        if image and image.filename:
            result = cloudinary.uploader.upload(
                image,
                folder="100-days-ai",
                transformation=[
                    {"width": 800, "height": 800, "crop": "fill", "gravity": "auto"}
                ],
            )
            image_url = result["secure_url"]

        slug = Project.make_slug(title)
        # Ensure unique slug
        existing = Project.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-day-{day_number}"

        project = Project(
            title=title,
            slug=slug,
            day_number=day_number,
            image_url=image_url,
            content=content,
        )
        db.session.add(project)
        db.session.commit()
        flash("Project created!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/edit.html", project=None)


@app.route("/admin/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def admin_edit(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        project.title = request.form.get("title", "").strip()
        project.day_number = request.form.get("day_number", type=int)
        project.content = request.form.get("content", "")

        image = request.files.get("image")
        if image and image.filename:
            result = cloudinary.uploader.upload(
                image,
                folder="100-days-ai",
                transformation=[
                    {"width": 800, "height": 800, "crop": "fill", "gravity": "auto"}
                ],
            )
            project.image_url = result["secure_url"]

        db.session.commit()
        flash("Project updated!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/edit.html", project=project)


@app.route("/admin/delete/<int:project_id>", methods=["POST"])
@login_required
def admin_delete(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# --- CLI Commands ---
@app.cli.command("init-db")
def init_db():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")


if __name__ == "__main__":
    app.run(debug=True)
