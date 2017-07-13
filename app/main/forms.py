from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp
from ..models import User, Role
from flask_pagedown.fields import PageDownField

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must \
                                          have only letters, numbers, dots or underscores \
                                          and must begin with letters.')])
    confirmed = BooleanField('confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)

        # to implement `SelectField` member. 
        self.role.choices = [(role.id, role.name) \
                             for role in Role.query.order_by(Role.name).all()]
        
        # in order to implement custome validate methods, we should take user object 
        # as a member variable.
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
 
    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class PostForm(FlaskForm):
    body = StringField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('Comment here', validators=[Required()])
    submit = SubmitField('Submit')