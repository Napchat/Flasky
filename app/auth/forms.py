from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField(
        'Email', 
        validators=[Required(), Length(1, 64), Email()]
    )

    username = StringField(
        'Username', 
        validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must \
                                                      have only letters, numbers, dots or underscores \
                                                      and must begin with letters.')]
    )

    # password should be input twice as a safety measure.
    # `EqualTo` validator is attached to one of the password
    # fields with the name of the other field given as an argument
    password = PasswordField(
        'Password', 
        validators=[Required(), EqualTo('password2', message='Passwords must match.')]
    )

    password2 = PasswordField('Confirm password', validators=[Required()])

    submit = SubmitField('Register')

    # a method with the prefix `validate_` followed by the name of a
    # field is invoked in addition to any regularly defined validators.
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('OldPassword', validators=[Required()])
    new_password = PasswordField('NewPassword', validators=[
        Required(), EqualTo('new_password2', message='Passwords must match.')])
    new_password2 = PasswordField('Confirm New Password', validators=[Required()])
    submit = SubmitField('Confirm')