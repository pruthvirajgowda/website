from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from forms import CreatePostForm, CreateContactForm, LoginForm, RegisterForm, CommentForm
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_gravatar import Gravatar
import datetime

year = datetime.datetime.now().year

app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = "pruthvi"

login_manager = LoginManager()
login_manager.init_app(app)


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    def get_id(self):
        return self.id


class BlogPost(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="posts")
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


class ContactForms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    ph_no = db.Column(db.Integer, nullable=False)
    msg = db.Column(db.String, nullable=False)


db.create_all()


@app.route('/index')
@app.route('/')
def home():
    post_objects = BlogPost.query.all()
    return render_template("index.html", all_posts=post_objects, year=year, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", year=year, current_user=current_user)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    contact_form = CreateContactForm()
    if contact_form.validate_on_submit():
        new_contact = ContactForms(
            name=contact_form.name.data,
            email=contact_form.email.data,
            ph_no=contact_form.ph_no.data,
            msg=contact_form.msg.data
        )
        db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for("contact"))
    return render_template("contact.html", year=year, form=contact_form, current_user=current_user)


@app.route("/post/<int:post_id>/<int:author_id>", methods=["POST", "GET"])
def show_post(post_id, author_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to Login! or Register to comment")
            return redirect(url_for("login"))
        new_comment = Comment(
            text=form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
            )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", author_id=author_id, post_id=post_id))
    return render_template("post.html", post=requested_post, year=year, current_user=current_user, author_id=author_id,
                           form=form)


@app.route("/new-post", methods=['POST', 'GET'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            author=current_user,
            img_url=form.img_url.data,
            date=datetime.date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form, year=year, current_user=current_user)


@app.route('/edit-post/<int:post_id>/<int:author_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id, author_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id, author_id=author_id))
    return render_template("make-post.html", form=edit_form, is_edit=True, year=year, current_user=current_user)


@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            redirect(url_for("login"))

        hashed_salted_password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=form.email.data, name=form.name.data, password=hashed_salted_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, year=year, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email doesn't exist. Try again!")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Password doesn't match. Try again!")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form, current_user=current_user, year=year)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
