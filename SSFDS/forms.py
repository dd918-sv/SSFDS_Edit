from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SSFDS.models import User, Restaurant


class RestaurantRegistrationForm(FlaskForm):
    username = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
        
    def validate_email(self, email):
        restaurant = Restaurant.query.filter_by(email=email.data).first()
        user = User.query.filter_by(email=email.data).first()
        if restaurant:
            raise ValidationError('That email is taken. Please choose a different one.')
        elif user:
            raise ValidationError('That email is taken. Please choose a different one.')


class UserRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    ngo = BooleanField('Are you an NGO?')
    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        restaurant = Restaurant.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        elif restaurant:
            raise ValidationError('That email is taken. Please choose a different one.')
        

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    picture= FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        user = current_user
        if username.data!= current_user.username and isinstance(user, User):
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data!= current_user.email:
            user = User.query.filter_by(email=email.data).first()
            restaurant = Restaurant.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            elif restaurant:
                raise ValidationError('That email is taken. Please choose a different one.')
