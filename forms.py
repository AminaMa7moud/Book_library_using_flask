from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, SubmitField , PasswordField , BooleanField
from wtforms.validators import DataRequired, Length, NumberRange , Email, EqualTo
from flask_wtf.file import FileField, FileAllowed

# USER LOG IN
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


# USER REGISTER
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

# Author
class AuthorForm(FlaskForm):
    name = StringField("Author Name", validators=[DataRequired(), Length(min=2, max=255)])
    submit = SubmitField("Add Author")


# BOOK
class BookForm(FlaskForm):
    name = StringField("Book Name", validators=[DataRequired(), Length(min=2, max=255)])
    publish_date = DateField("Publish Date (YYYY-MM-DD)", format="%Y-%m-%d", validators=[DataRequired()])
    price = DecimalField("Price", places=2, validators=[DataRequired(), NumberRange(min=0, message="Price must be positive")])
    appropriate = SelectField(
        "Appropriate For",
        choices=[('Under 8', 'Under 8'), ('8-15', '8-15'), ('Adults', 'Adults')],
        default='Adults',
        validators=[DataRequired()]
    )
    author_id = SelectField("Select Author", coerce=int, validators=[DataRequired()])
    img = FileField("Book Cover (JPG or PNG)", validators=[FileAllowed(['jpg', 'png'], "Only images allowed!")])
    submit = SubmitField("Add Book")
