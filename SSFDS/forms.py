from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,IntegerField, FloatField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,NumberRange,Length
from SSFDS.models import User, Restaurant,Order
from SSFDS import bcrypt


# Registration form for restaurants to create a new account.

# Contains fields for name, email, address, password,
# and password confirmation. Validates that email is not
# already in use by another restaurant or user.

class RestaurantRegistrationForm(FlaskForm):
    username = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password'),Length(min=8,max=12)])
    submit = SubmitField('Sign Up')
        
    def validate_email(self, email):
        restaurant = Restaurant.query.filter_by(email=email.data).first()
        user = User.query.filter_by(email=email.data).first()
        if restaurant:
            raise ValidationError('That email is taken. Please choose a different one.')
        elif user:
            raise ValidationError('That email is taken. Please choose a different one.')


# User registration form that validates username and email are unique.

# Contains fields for username, email, address, password, confirm password,
# and whether the user is an NGO. Validates that username and email are
# not already in use by another user or restaurant.

class UserRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=12)])
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

# This form allows users to update their profile information. It validates that 
# the username and email are unique, and that the current user's password is correct
# if they are changing their password. It also requires the user to enter their 
# location before submitting the form.
class UpdateForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    picture= FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    recaptcha = RecaptchaField()
    submit = SubmitField('Update')
    
    def validate_password(self, password):
        if not bcrypt.check_password_hash(current_user.password, password.data):
            raise ValidationError('Invalid password')
    
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

# AddDishForm class:

# This form allows a restaurant user to add a new dish to the menu. It has the following fields:

# - name: The name of the dish
# - price: The price of the dish  
# - description: A short description of the dish
# - picture: An image file to upload for the dish
# - submit: The submit button to add the dish

# The name, price, and picture fields are required. The description has length validation.

class AddDishForm(FlaskForm):
    name=StringField('Dish Name',validators=[DataRequired()])
    price=FloatField('Price',validators=[DataRequired()])
    quantity=IntegerField('Quantity',validators=[DataRequired(),NumberRange(min=1)])
    description = StringField('Description',validators=[Length(min=0,max=30)])
    picture= FileField('Add Dish Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit=SubmitField('Add Dish')

# ForgotPasswordForm class.

# This form is used when a user has forgotten their password. It contains:

# - email: The user's email address, to identify their account. Required and validated.  
# - submit: The submit button to send the reset password email.

# The validate_email method checks that a user account exists with
# the given email, otherwise it raises a ValidationError.

class ForgotPasswordForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        restaurant = Restaurant.query.filter_by(email=email.data).first()

        if user is None and restaurant is None:
            raise ValidationError('There is no account with that email. You must register first.')

# ResetPasswordForm class

# This form is used when a user is resetting their password. It contains:

# - password: The new password entered by the user. Required and validated.
# - confirmPassword: A field to confirm the new password. Required, validated and must match password. 
# - submit: The submit button to reset the password.
class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirmPassword=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Reset Password')

# DonationForm class

# This form is used to collect donations. It contains:

# - amount: The donation amount entered by the user, required and validated.
# - submit: The submit button to complete the donation.

# The amount is validated to be between 100 and 100000000.
class DonationForm(FlaskForm):
    amount=FloatField('Amount',validators=[DataRequired()])
    submit=SubmitField('Donate')

    def validate_amount(self, amount):
        if amount.data<100:
            raise ValidationError('Minimum amount is 100')
        elif amount.data>100000000:
            raise ValidationError('Maximum amount is 100000000')

# Validates that the end time is after the start time.
# Raises a ValidationError if end time is not greater than start time.
def validate_timings(form, field):
    start_time = form.start.data
    end_time = form.end.data

    if start_time >= end_time:
        raise ValidationError('End time should be greater than start time.')

# TimeForm class
# 
# This form contains fields to enter a start and end time.
#
# It validates that the end time is after the start time using the validate_timings validator. 
#
# Attributes:
#   start: Start time field, required and formatted as HH:MM  
#   end: End time field, required, formatted as HH:MM, and validated to be after start time
#   submit: Submit button for the form

class TimeForm(FlaskForm):
    start = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end = TimeField('End Time', format='%H:%M', validators=[DataRequired(), validate_timings])
    submit = SubmitField('Submit')

class CartForm(FlaskForm):
    
    quantity = IntegerField('Quantity', validators=[DataRequired(),NumberRange(min=1)])
    submit = SubmitField('Add to Cart')