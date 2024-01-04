from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField
from wtforms.validators import DataRequired, equal_to, ValidationError, length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class SearchForm(FlaskForm):
    searched = StringField("search", validators=[DataRequired()])
    submit = SubmitField('Submit')


class post_form(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


class user_form(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    color = StringField("Favorite color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password', validators=[DataRequired(), equal_to('password_hash2', message="password must match")])
    password_hash2 = PasswordField('Confirm password', validators=[DataRequired()])
    profile_pic = FileField("Profile_pic")
    submit = SubmitField('Submit')

class name_form(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    submit = SubmitField('Submit')


class pw_form(FlaskForm):
    email = StringField("Enter your email :", validators=[DataRequired()])
    password_hash = PasswordField(
        "Enter your password :", validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField("Enter username :", validators=[DataRequired()])
    password = PasswordField("Enter your password :",
                             validators=[DataRequired()])
    submit = SubmitField('Submit')