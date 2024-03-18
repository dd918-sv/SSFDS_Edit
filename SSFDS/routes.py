import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from SSFDS import app, db, bcrypt
from SSFDS.forms import RestaurantRegistrationForm, UserRegistrationForm, LoginForm, UpdateForm
from SSFDS.models import Restaurant, User, Dish
from flask_login import login_user, current_user, logout_user, login_required



restaurants = [
    {
        'name': 'Corey Schafer',    
        'description': 'Blog Post 1',
        'content': 'First post content'
    },
    {
        'name': 'la chafer',
        'description': 'fa  Post 1',
        'content': 'Fi second content'
    }
]

def identity():
    return len(User.query.all())+len(Restaurant.query.all())+1

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', restaurants=restaurants)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/RestaurantRegister", methods=['GET', 'POST'])
def restaurantregister():
    if(current_user.is_authenticated):
        return redirect(url_for('home'))
    form = RestaurantRegistrationForm()
    if form.validate_on_submit():
        hashedPassword=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        restaurant = Restaurant(id= identity(), username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data)
        db.session.add(restaurant)
        db.session.commit()
        flash('Your account has been created! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('restaurantRegister.html', title='Register', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if(current_user.is_authenticated):
        return redirect(url_for('home'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashedPassword=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        restaurant = User(id= identity(), username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data, ngo=form.ngo.data)
        db.session.add(restaurant)
        db.session.commit()
        flash('Your account has been created! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('userRegister.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if(current_user.is_authenticated):
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        restaurant=Restaurant.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successful','success') 
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        elif restaurant and bcrypt.check_password_hash(restaurant.password, form.password.data):
            login_user(restaurant, remember=form.remember.data)
            flash('Login Successful','success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/print")
def prints():
    print(User.query.all())
    return "print"

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(formPicture):
    randomHex=secrets.token_hex(8)
    _, fExt = os.path.splitext(formPicture.filename)
    pictureName = randomHex + fExt
    picturePath = os.path.join(app.root_path,'static/profile_pics', pictureName)
    outputSize=(125,125)
    resizedImage = Image.open(formPicture)
    resizedImage.thumbnail(outputSize)
    resizedImage.save(picturePath)
    return pictureName

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = save_picture(form.picture.data)
            current_user.image = pictureFile
            print(current_user.image)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data = current_user.address
    image = url_for('static', filename='profile_pics/' + current_user.image)
    usertype = None
    if isinstance(current_user, User):
        if current_user.ngo == 'True':
            usertype = "NGO"
        else:
            usertype = "Customer"
    else:
        usertype = "Restaurant"
    return render_template('account.html', image = image, form = form, usertype = usertype)
        
    
