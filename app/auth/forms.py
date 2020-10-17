from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField(u'Username', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    fullname = StringField(u'Full Name', validators=[DataRequired()])
    student_number = StringField(u'Student Number', validators=[DataRequired()])
    password = PasswordField(u'Password', validators=[DataRequired()])
    password2 = PasswordField(
        u'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    submit = SubmitField(u'Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(u'Password', validators=[DataRequired()])
    password2 = PasswordField(
        u'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(u'Request Password Reset')


class ChangePasswordForm(FlaskForm):
    password = PasswordField(u'Password', validators=[DataRequired()])
    password2 = PasswordField(
        u'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(u'Change My Password')


class ChangeFullnameForm(FlaskForm):
    fullname = StringField(u'Full Name', validators=[DataRequired()])
    submit = SubmitField(u'Change My Fullname')
