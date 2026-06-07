from datetime import date, datetime
from flask import (
    Flask,
    abort,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
)
import bleach
from flask_bootstrap import Bootstrap5
from flask_gravatar import Gravatar
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, CommentForm
from forms import CreatePostForm
import os


SAMPLE_POSTS = [
    {
        "title": "Building AI-Assisted Web Apps with Flask in 2026",
        "subtitle": "How LLM APIs and Flask fit together for practical side projects",
        "date": "May 18, 2026",
        "img_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80",
        "body": (
            "<p>Flask remains one of the fastest ways to ship a Python web app—and in 2026, "
            "pairing it with AI APIs opens creative doors without heavy infrastructure.</p>"
            "<p>Start with a thin service layer: keep prompts, model calls, and rate limiting "
            "outside your route handlers. Use environment variables for API keys, cache common "
            "responses, and always validate user input before sending it to a model.</p>"
            "<p>For blog platforms like this one, AI can help draft outlines, suggest titles, "
            "or summarize long posts—but the author's voice should stay in control. The best "
            "AI-assisted apps feel fast, transparent, and respectful of user data.</p>"
        ),
    },
    {
        "title": "Python 3.13 and the Future of Backend Development",
        "subtitle": "Performance gains, typing improvements, and what they mean for Flask devs",
        "date": "May 12, 2026",
        "img_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=80",
        "body": (
            "<p>Each Python release brings incremental wins for backend developers. "
            "Faster startup, better error messages, and stronger typing support mean "
            "cleaner Flask codebases with fewer surprises in production.</p>"
            "<p>If you maintain a blog or API, schedule regular dependency updates, "
            "pin versions in requirements.txt, and run smoke tests after upgrades. "
            "Small, frequent updates beat painful yearly migrations.</p>"
        ),
    },
    {
        "title": "Deploying Flask on Render: A Student's Zero-Downtime Checklist",
        "subtitle": "From local SQLite to a live URL without losing your mind",
        "date": "May 05, 2026",
        "img_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80",
        "body": (
            "<p>Deploying your first Flask app is a milestone. Render makes it approachable: "
            "connect your GitHub repo, set environment variables, and define a start command "
            "in the Procfile.</p>"
            "<p>Move from SQLite to PostgreSQL before going live, set SECRET_KEY and database "
            "URLs in the dashboard, and enable automatic deploys only after your build passes "
            "locally. Health checks and logging early will save hours of debugging later.</p>"
        ),
    },
    {
        "title": "Cursor, Copilot, and the New Developer Workflow",
        "subtitle": "AI pair programming is here—how to use it without skipping the fundamentals",
        "date": "April 28, 2026",
        "img_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&q=80",
        "body": (
            "<p>AI coding assistants are changing how we write software—but they do not replace "
            "understanding architecture, security, or debugging skills.</p>"
            "<p>Use them to explore APIs, generate boilerplate, and refactor repetitive code. "
            "Always review suggestions, run tests, and learn why a solution works. The developers "
            "who thrive in 2026 combine AI speed with solid computer science fundamentals.</p>"
        ),
    },
]


ALLOWED_HTML_TAGS = [
    "p", "br", "strong", "em", "u", "s", "a", "ul", "ol", "li",
    "h1", "h2", "h3", "blockquote", "pre", "code",
]
ALLOWED_HTML_ATTRS = {"a": ["href", "title", "target", "rel"]}


def sanitize_html(content):
    if not content:
        return ""
    return bleach.clean(
        content,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRS,
        strip=True,
    )


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = "login"


class Base(DeclarativeBase):
    pass


# Gravator
gravatar = Gravatar(app, size=100, rating='g', default='retro')
# CREATE DATABASE
# Fetch variables


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URl", DATABASE_URL)
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(300), nullable=False)
    is_author: Mapped[int] = mapped_column(Integer, default=0)
    is_admin: Mapped[int] = mapped_column(Integer, default=0)

    # ralations
    posts = db.relationship("BlogPosts", back_populates="author")
    comments = db.relationship("Comments", back_populates="author")


class BlogPosts(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0)

    author = db.relationship("Users", back_populates="posts")
    comments = db.relationship("Comments", back_populates="post")


class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(300), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("blog_posts.id"))

    # relation ship
    post = db.relationship("BlogPosts", back_populates="comments")
    author = db.relationship("Users", back_populates="comments")


# TODO: Create a User table for all your registered users.


def ensure_author():
    author = db.session.execute(db.select(Users).limit(1)).scalar_one_or_none()
    if author:
        return author
    author = Users(
        name="Sayed Mohammad Hashimi",
        email="admin@hashimi.blog",
        password=generate_password_hash(
            os.getenv("DEMO_ADMIN_PASSWORD", "ChangeMe123!"),
            salt_length=8,
        ),
    )
    db.session.add(author)
    db.session.commit()
    return author


def seed_sample_posts():
    """Add demo articles when sample titles are missing."""
    author = ensure_author()

    existing_titles = {
        title
        for title in db.session.execute(db.select(BlogPosts.title)).scalars().all()
    }

    for post_data in SAMPLE_POSTS:
        if post_data["title"] in existing_titles:
            continue
        db.session.add(
            BlogPosts(
                title=post_data["title"],
                subtitle=post_data["subtitle"],
                date=post_data["date"],
                body=post_data["body"],
                img_url=post_data["img_url"],
                author=author,
            )
        )
        existing_titles.add(post_data["title"])

    db.session.commit()


with app.app_context():
    db.create_all()
    seed_sample_posts()


@app.context_processor
def inject_globals():
    return {"now_year": datetime.now().year}


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')
# TODO: Use Werkzeug to hash the user's password when creating a new user.


@app.route("/register", methods=["GET", "POST"])
def register():
    print("DATABASE URL:", app.config["SQLALCHEMY_DATABASE_URI"])
    print(db.engine.url)
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print(form.email.data)
            with app.app_context():
                user = Users.query.filter_by(email=form.email.data).first()
                if not user:
                    user = Users(
                        email=form.email.data.lower(),
                        password=generate_password_hash(
                            f"{form.password.data}", salt_length=8
                        ),
                        name=form.name.data,
                    )

                    db.session.add(user)
                    print(f"user added{user}")
                    db.session.commit()
                    print(f"user commited{user}")
                    login_user(user)
                    print(f"user logged in{user}")
                    return redirect(url_for("get_all_posts"))
                else:
                    flash("This email has allready an acount")
                    return redirect(url_for("login"))
    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email.
@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = db.session.execute(
                db.select(Users).where(Users.email == form.email.data)
            ).scalar()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for("get_all_posts"))
                else:
                    flash("The email or password is incorrect!")
            else:
                flash("The email or password is incorrect!")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


@app.route("/")
def get_all_posts():
    result = db.session.execute(
        db.select(BlogPosts).order_by(BlogPosts.id.desc())
    )
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    make_comment = CommentForm()
    all_comments = db.session.execute(
        db.select(Comments).where(Comments.post_id == post_id)).scalars()
    requested_post = db.get_or_404(BlogPosts, post_id)
    requested_post.views += 1
    db.session.commit()
    return render_template("post.html", post=requested_post, comment_form=make_comment, all_comments=all_comments, gravatar=gravatar)


# TODO: Use a decorator so only an admin user can create a new post
def only_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        if current_user.is_admin == 1:
            return func(*args, **kwargs)
        return abort(403)

    return wrapper


def only_author(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        if current_user.is_author == 1:
            return func(*args, **kwargs)
        return abort(403)

    return wrapper


@app.route("/new-post", methods=["GET", "POST"])
@only_author
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPosts(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=sanitize_html(form.body.data),
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@only_admin
def edit_post(post_id):
    post = db.get_or_404(BlogPosts, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = sanitize_html(edit_form.body.data)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post


@app.route("/delete/<int:post_id>")
@only_admin
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPosts, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route('/comment', methods=['POST'])
@login_required
def save_comment():
    post_id = request.args.get("p")
    form = CommentForm()
    if form.validate_on_submit():
        db.session.add(
            Comments(
                text=sanitize_html(form.comment_text.data),
                author_id=current_user.id,
                post_id=post_id,
            )
        )
        db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@login_manager.user_loader
def load_user(id):
    return Users.query.filter_by(id=int(id)).first()


if __name__ == "__main__":
    app.run(debug=True, port=5002)
