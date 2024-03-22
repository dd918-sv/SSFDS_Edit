from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SSFDS.models import User, Restaurant
from SSFDS import bcrypt


class RestaurantRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
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
    password = PasswordField('Enter Password To Update Details', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_password(self, password):
        if not bcrypt.check_password_hash(current_user.password, password.data):
            raise ValidationError('Invalid password')
    
    def validate_username(self, username):
        if username.data!= current_user.username and isinstance(current_user,User):
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

class AddDishForm(FlaskForm):
    name=StringField('Dish Name',validators=[DataRequired()])
    price=FloatField('Price',validators=[DataRequired()])
    description = StringField('Description',validators=[Length(min=0,max=30)])
    submit=SubmitField('Add Dish')

class ForgotPasswordForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        restaurant = Restaurant.query.filter_by(email=email.data).first()

        if user is None and restaurant is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirmPassword=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Reset Password')

class DonationForm(FlaskForm):
    amount=FloatField('Amount',validators=[DataRequired(),])
    submit=SubmitField('Donate')

    def validate_amount(self, amount):
        if amount.data<100:
            raise ValidationError('Minimum amount is 100')
        elif amount.data>100000000:
            raise ValidationError('Maximum amount is 100000000')