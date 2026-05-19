from datetime import date
from xml.etree.ElementTree import Comment
from flask import (
    Flask,
    abort,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
)
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
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
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = "login"

# Gravator
gravatar = Gravatar(app, size=100, rating='g', default='retro')
# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
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


with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
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
                    db.session.commit()
                    login_user(user)
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
            )
            if user:
                user = user.scalar()
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
    result = db.session.execute(db.select(BlogPosts))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    make_comment = CommentForm()
    all_comments = db.session.execute(
        db.select(Comments).where(Comments.post_id == post_id)).scalars()
    requested_post = db.get_or_404(BlogPosts, post_id)
    return render_template("post.html", post=requested_post, comment_form=make_comment, all_comments=all_comments, gravatar=gravatar)


# TODO: Use a decorator so only an admin user can create a new post
def only_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user:
            if current_user.id == 1:
                return func(*args, **kwargs)
            else:
                return abort(403)
        return redirect(url_for("login"))

    return wrapper


@app.route("/new-post", methods=["GET", "POST"])
@only_admin
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPosts(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
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
        post.author = current_user.id
        post.body = edit_form.body.data
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
        with app.app_context():
            print(form.comment_text, current_user.id, post_id)
            db.session.add(
                Comments(text=form.comment_text.data, author_id=current_user.id, post_id=post_id,),)
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
