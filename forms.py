from flask_wtf import FlaskForm
from wtforms import * #StringField, BooleanField, PasswordField, TextAreaField, EmailField, validators, DateField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.validators import Email, InputRequired, ValidationError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from models import User, Site

#import wtforms.QuerySelectField
# Set your classes here.


class RegisterForm(FlaskForm):
    name = StringField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = EmailField(
        'Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=250)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )

    def validate_email(form, field):
        user = User.query.filter(User.email == field.data).first()
        if user is not None:
            raise ValidationError("A user with that email already exists")

class LoginForm(FlaskForm):
    name = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    # WTForms supports "inline" validators
    # which are methods of our `Form` subclass
    # with names in the form `validate_[fieldname]`.
    # This validator will run after all the
    # other validators have passed.
    def validate_password(form, field):
        try:
            user = User.query.filter(User.email == form.email.data).one()
        except (MultipleResultsFound, NoResultFound):
            raise ValidationError("Invalid user")
        if user is None:
            raise ValidationError("Invalid user")
        if not user.is_valid_password(form.password.data):
            raise ValidationError("Invalid password")

        # Make the current user available
        # to calling code.
        form.user = user

class ForgotForm(FlaskForm):
    email = EmailField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )

class VisitForm(FlaskForm):
    browser = StringField()
    date = DateField()
    event = StringField()
    url = StringField()
    ip_address = StringField("IP Address")
    site = SelectField(query_factory=lambda: Site.query.all())