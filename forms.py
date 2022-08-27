from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL, Email, InputRequired
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField("Blog post title", validators=[DataRequired()])
    subtitle = StringField("Blog subtitle", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    img_url = StringField("Blog background image url", validators=[URL()])
    author = StringField("Your name", validators=[DataRequired()])
    submit = SubmitField("submit post")


class CreateContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    ph_no = StringField("Phone Number", validators=[DataRequired()])
    msg = StringField("Message", validators=[DataRequired()])
    submit = SubmitField("submit")


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), InputRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), InputRequired()])
    submit = SubmitField("Sign me up!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let me in!")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("submit comment")
