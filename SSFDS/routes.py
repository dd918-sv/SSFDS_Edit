import os
import secrets
from datetime import datetime,time
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from SSFDS import app, db, bcrypt, mail
from SSFDS.forms import RestaurantRegistrationForm, UserRegistrationForm, LoginForm, UpdateForm, AddDishForm, ForgotPasswordForm, ResetPasswordForm, DonationForm,TimeForm,CartForm
from SSFDS.models import Restaurant, User, Dish, Transaction, Order, Donation,Time
from flask_login import login_user, current_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from math import radians, sin, cos, sqrt, atan2, ceil

global start
global end
start=time(16, 0)
end=time(21, 0)

# Checks if the given time is between the start and end times.
#
# Args:
#   start_time (datetime.time): The start time to check against. 
#   end_time (datetime.time): The end time to check against.
#
# Returns:
#   bool: True if check_time is between start_time and end_time, False otherwise.

def is_time_between(start_time, end_time):
    check_time = datetime.now().time()
    return start_time <= check_time <= end_time


# Returns the next available unique ID by counting all Users, Restaurants, and adding 1. 

# This provides a simple way to get a unique numeric ID for new objects.

def identity():
    return len(User.query.all())+len(Restaurant.query.all())+1

# Renders the home page. 
# If the user is authenticated and an admin, redirects to the admin page.
# If the user is authenticated but has no location set, flashes a warning to set location and redirects to account page.
# Otherwise, fetches all restaurants or only nearby restaurants based on auth status,  
# fetches all transactions, and renders the home template.
@app.route("/")
@app.route("/home")
def home():
    user=current_user
    restaurants=None
    if(user.is_authenticated and user.id==1):
        return redirect(url_for('admin'))
    if(user.is_authenticated and (user.latitude is None or user.longitude is None)):
        if(isinstance(user, User)):
            flash('Please enter your location first in Account settings for getting list of restaurants','warning')
        else:
            flash('Please enter your location first in Restaurant settings for getting list of orders','warning')
        return redirect(url_for('account'))
    elif(user.is_authenticated):
        restaurants = Restaurant.query.filter(Restaurant.latitude.isnot(None),Restaurant.longitude.isnot(None)).all()
    else:
        restaurants = Restaurant.query.all()
    transactions = Transaction.query.all()
    return render_template('home.html', restaurants=restaurants,title='Home',calculate_distance=calculate_distance,transactions=transactions)

   
# Checks if the current user is an admin and redirects them to the admin page.
# 
# If the current user is not admin, redirects to the home page.

@app.route("/admin")
@login_required
def admin():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        return render_template('admin.html', title='Admin')

# Renders a page showing all restaurants.

# If the user is not an admin, redirects to the home page.  
# Otherwise, fetches all restaurants from the database and renders the allRestaurants template.

@app.route("/allRestaurants")
@login_required
def allRestaurants():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        restaurants=Restaurant.query.all()
        return render_template('allRestaurants.html', restaurants=restaurants,title='All Restaurants')

# Renders a page showing all users except the admin.

# If the current user is not admin, redirects to the home page.
# Otherwise, fetches all users except the admin from the database and renders the allUsers template.

@app.route("/allUsers")
@login_required
def allUsers():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        users=User.query.filter_by(ngo=False).all()
        if len(users) > 0:
            users = users[1:]
        return render_template('allUsers.html', users=users,title='All Users')

# Renders a page showing all NGO users.

# If the current user is not admin, redirects to the home page.
# Otherwise, fetches all NGO users from the database and renders the allNgos template.

@app.route("/allNgos")
@login_required
def allNgo():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        ngos=User.query.filter_by(ngo=True).all()
        return render_template('allNgos.html', ngos=ngos,title='All Ngo')
    
@app.route("/allTransactions")
@login_required
def allTransactions():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        transactions=Transaction.query.all()
        transactions.reverse()
        setoforders=[]
        for transaction in transactions:
            orders=Order.query.filter_by(transactionID=transaction.id).all()
            setoforders.append(orders)
        size=len(transactions)
        return render_template('allTransactions.html', transactions=transactions, size=size, setoforders=setoforders, title='All Ngo')
    
# Renders a page to change the time window for ordering food.

# If the user is not admin, redirects to home page.
# Otherwise, displays a form to enter new start and end time.
# On submit, updates the time window in the database.

@app.route("/changetimewindow", methods=['GET', 'POST'])
@login_required
def changetimewindow():
    if(current_user.is_authenticated and current_user.id!=1):
        return redirect(url_for('home'))
    else:
        form = TimeForm()
        if form.validate_on_submit():
            start=form.start.data
            end=form.end.data
            print(start, end)
            timings=Time.query.all()
            if(timings==None or timings==[]):
                time=Time(start=start, end=end)
                db.session.add(time)
                db.session.commit()
            else:
                time=Time.query.first()
                time.start=start
                time.end=end
                db.session.commit()
            flash('Time window has been changed','success')
            return redirect(url_for('admin'))
        elif request.method == 'GET':
            time=Time.query.first()
            if(time!=None):
                form.start.data=time.start
                form.end.data=time.end
        return render_template('changetimewindow.html', title='Change Time Window', form=form)


# Renders about page.
@app.route("/about")
def about():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    return render_template('about.html', title='About')


# Registers a new restaurant user.

# - Checks if a user is already logged in and redirects to home if so.
# - Validates form data. 
# - Hashes password using bcrypt.
# - Creates new Restaurant object with form data.  
# - Adds new restaurant to database.
# - Flashes success message.
# - Redirects to login page.
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

# Registers a new user account.

# Checks if a user is already logged in and redirects to home if so. Validates form data.
# Hashes password using bcrypt. Creates new User object with form data.
# Adds new user to database. Flashes success message. Redirects to login page.
@app.route("/register", methods=['GET', 'POST'])
def register():
    if(current_user.is_authenticated):
        return redirect(url_for('home'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashedPassword=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(id= identity(), username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data, ngo=form.ngo.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('userRegister.html', title='Register', form=form)
# Logs in a user.

# Checks if a user is already logged in and redirects to home if so.
# Validates form data. Queries for User and Restaurant matching
# email. Checks hashed password against stored hash. If valid, logs in user.  
# Checks time if logging in restaurant user and restricts login window.
# Flashes success or failure message. Redirects to next page or home page.

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
            current_time = datetime.now()
            if 20 <= current_time.hour < 20.5 or 1:  
                login_user(restaurant, remember=form.remember.data)
                flash('Login Successful','success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Restaurant login is only available between 8 PM and 8:30 PM.', 'warning')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


# Logs out a user.
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# Saves the picture to the specified path.
def save_picture(formPicture, path):
    randomHex=secrets.token_hex(8)
    _, fExt = os.path.splitext(formPicture.filename)
    pictureName = randomHex + fExt
    picturePath = os.path.join(app.root_path, path, pictureName)
    outputSize=(125,125)
    resizedImage = Image.open(formPicture)
    resizedImage.thumbnail(outputSize)
    resizedImage.save(picturePath)
    return pictureName



# Renders the account page for the currently logged in user. 

# Allows the user to update their profile picture, username, email and address. 

# Checks if the user is an admin and redirects them to the admin page. 

# Saves any uploaded profile picture to the static/profile_pics folder.

# Shows the account type (Customer, Restaurant, NGO) based on the user object type.


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = save_picture(form.picture.data, 'static/profile_pics')
            current_user.image = pictureFile
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
        if current_user.ngo == True:
            usertype = "NGO"
        else:
            usertype = "Customer"
    else:
        usertype = "Restaurant"
    return render_template('account.html', image = image, form = form, usertype = usertype)


# Renders a form to allow a restaurant user to add a new dish. 

# Checks that the user is a restaurant, redirects regular users.

# Checks that the restaurant has location set in account. 

# Checks that the current time is within the allowed window set by the admin.

# Validates the form data and adds a new Dish object to the database.

# Saves any uploaded dish image and associates it with the Dish object.

# Adds success flash message on completion.

@app.route("/addDish", methods=['GET', 'POST'])
@login_required
def addDish():
    if(isinstance(current_user, User)):
        return redirect(url_for('home'))
    if current_user.latitude is None or current_user.longitude is None:
        flash('Please enter your location first in Account settings','warning')
        return redirect(url_for('account'))
    times=Time.query.first()
    if times==None or times.start==None or times.end==None:
                flash('Restaurant\'s can not add plates currently. Try contacting the administrator.','warning')
                return redirect(url_for('account'))
    elif not is_time_between(times.start, times.end):
        flash(f'Restaurant\'s can add plates only between {(times.start).strftime("%I:%M %p")} and {(times.end).strftime("%I:%M %p")}.', 'warning')
        return redirect(url_for('account'))
    form=AddDishForm()
    if form.validate_on_submit():
        dish=Dish(name=form.name.data,price=form.price.data,quantityAvailable=form.quantity.data,description=form.description.data,restaurant=current_user)
        if form.picture.data:
            pictureFile = save_picture(form.picture.data, 'static/dish_pics')
            dish.image = pictureFile
        db.session.add(dish)
        db.session.commit()
        flash('Dish added successfully','success')
        return redirect(url_for('account'))
    return render_template('/addDish.html',form=form)

# Deletes a dish from the menu
@app.route("/delete-dish/<int:restaurant_id>/<int:dish_id>", methods=['DELETE'])
def delete_dish(restaurant_id, dish_id):
    dish = Dish.query.filter_by(id=dish_id, restaurantID=restaurant_id).first_or_404()
    if dish:
        db.session.delete(dish)
        db.session.commit()
        flash('The dish has been deleted!', 'success')
        return jsonify({'redirect_url': url_for('account')}), 200


# Sends mail to the user for resetting password  
def sendMail(user):
    token=user.get_token()
    msg=Message('Password Reset Request',recipients=[user.email],sender='priorityencoder@gmail.com')
    msg.body=f'''To reset your password, visit the following link:
    {url_for('reset_token',token=token,_external=True)}
    '''
    mail.send(msg)

# Renders forgot password page
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    form=ForgotPasswordForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        restaurant=Restaurant.query.filter_by(email=form.email.data).first()
        if user:
            sendMail(user)
            flash('An email has been sent to your email address with instructions to reset your password','success')
            return redirect(url_for('login'))
        elif restaurant:
            sendMail(restaurant)
            flash('An email has been sent to your email address with instructions to reset your password','success')
            return redirect(url_for('login')) 
        else:
            flash('Email not found','danger')
    return render_template('forgotPassword.html',title='Reset Password',form=form)

# renders reset password page
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user=User.verify_token(token)
    restaurant=Restaurant.verify_token(token)
    if user is None and restaurant is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('forgotPassword'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashedPassword=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if user is not None:
            user.password=hashedPassword
        elif restaurant is not None:
            restaurant.password=hashedPassword
        db.session.commit()
        flash('Your password has been updated! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('resetPassword.html',title='Reset Password',form=form)
        
# Renders Donations Received page for the NGO
@app.route('/DonationsReceived')
@login_required
def DonationsReceived():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if(isinstance(user, User) and current_user.ngo==True):
        donations=Donation.query.filter_by(ngoID=current_user.id).all()
        return render_template('DonationsReceived.html',title='Donations Received',donations=donations)
    else:
        return redirect(url_for('home'))


# Renders Donations Given Page for the customer
@app.route('/DonationsGiven')
@login_required
def DonationsGiven():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if(isinstance(user, User) and current_user.ngo==False):
        donations=Donation.query.filter_by(userID=current_user.id).all()
        return render_template('DonationsGiven.html',title='Donations Given',donations=donations)
    else:
        return redirect(url_for('home'))
    

# Renders Donate page for customer
@app.route('/Donate')
@login_required
def Donate():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if(isinstance(user, User) and current_user.ngo==False):
        ngos=User.query.filter_by(ngo=True).all()
        return render_template('Donate.html',title='Donate', ngos=ngos)
    else:
        return redirect(url_for('home'))

# Function for implementing donation
@app.route('/Donate/<int:ngo_ID>', methods=['GET', 'POST'])
@login_required
def DonateToNGO(ngo_ID):
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if(isinstance(user, User) and current_user.ngo==False):
        ngo=User.query.filter_by(id=ngo_ID).first()
        form=DonationForm()
        if form.validate_on_submit():
            donation=Donation(userID=current_user.id,ngoID=ngo_ID,amount=form.amount.data, date=datetime.now())
            db.session.add(donation)
            db.session.commit()
            flash('Donation has been made','success')
            return redirect(url_for('Donate'))
        return render_template('DonateToNGO.html',title='Donate', ngo=ngo, form=form)
    else:
        return redirect(url_for('home'))

# Renders Map
@app.route('/map')
def map():
    return render_template('map.html')

# Function for saving location
@app.route('/location', methods=['POST'])
def location():
    lat = request.form['lat']
    lng = request.form['lng']
    current_user.latitude = lat
    current_user.longitude = lng
    db.session.commit()
    return render_template('location_saved.html', lat=lat, lng=lng)

# Renders menu for the customer/NGO
@app.route("/menu/<int:restaurant_id>")
@login_required
def menu(restaurant_id):
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    if(isinstance(current_user,Restaurant)):
        return redirect(url_for('home'))
    elif current_user.latitude is None or current_user.longitude is None:
        flash('Please enter your location first in Account settings','warning')
        return redirect(url_for('home'))
    restaurant=Restaurant.query.get(restaurant_id)
    dishes=Dish.query.filter_by(restaurantID=restaurant_id).all()
    discount=None
    if(current_user.ngo):
        discount=40
    else:
        discount=20
    return render_template('menu.html',restaurant=restaurant,dishes=dishes, discount=discount)

# Function for adding to cart
@app.route("/addToCart/<int:restaurant_id>/<int:user_id>/<int:dish_id>", methods=['POST', 'GET'])
@login_required
def addToCart(restaurant_id, user_id, dish_id):
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    if isinstance(current_user, Restaurant):
        flash('A restaurant is not allowed to order!', 'warning')
        return redirect(url_for('home'))

    transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
    
    if transaction is None:
        transaction = Transaction(userID=user_id, restaurantID=restaurant_id, paymentMethod='cash', paid=False, orderplaced=False, discount=0,review='')
        if current_user.ngo:
            transaction.discount = 40
        else:
            transaction.discount = 20
        db.session.add(transaction)
        db.session.commit()
        order = Order(transactionID=transaction.id, dishID=dish_id, quantity=1)
        db.session.add(order)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully Added', 'quantity': 1})
    else:
        checkOrder = Order.query.filter_by(transactionID=transaction.id).all()
        if checkOrder:
            for order in checkOrder:
                if order.dish.restaurantID != restaurant_id:
                    return jsonify({'success':False,'message':'You cannot add dishes from different restaurants in the same order. Either complete your current order or empty your cart.'})
        checkOrder = Order.query.filter_by(transactionID=transaction.id, dishID=dish_id).first()
        if checkOrder:
            return jsonify({'success': False, 'message': 'Already Added'})
        else:
            order = Order(transactionID=transaction.id, dishID=dish_id, quantity=1)
            db.session.add(order)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Successfully Added', 'quantity': 1})    
    
    
# Renders go to cart page
@app.route("/goToCart", methods=['GET', 'POST'])
@login_required
def goToCart():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user_id = current_user.id
    user=current_user
    transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
    if transaction is None:
        flash('Your Cart is empty.', 'warning')
        return redirect(url_for('home'))
    
    orders = Order.query.filter_by(transactionID=transaction.id).all()
    if orders is None or orders == []:
        flash('Your Cart is empty.', 'warning')
        return redirect(url_for('home'))
    order=orders[0]
    restaurant=order.transaction.restaurant
    distance=calculate_distance(restaurant.latitude,restaurant.longitude,user.latitude,user.longitude)
    delivery_charge=0
    discount=transaction.discount
    if distance>2:
        delivery_charge=(5*(ceil(distance-2)))
    form=CartForm()
    return render_template('cart.html', orders=orders,delivery_charge=delivery_charge, title='Cart', discount=discount,form=form)

# Function for dynamic updation of quantity
@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    data = request.get_json()
    order_id = data.get('order_id')
    quantity = data.get('quantity')
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
    order.quantity = quantity
    db.session.commit()
    return jsonify({"success": True}), 200

# Function for removal of a dish from the cart
@app.route("/remove_order/<int:order_id>", methods=['POST'])
@login_required
def remove_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash('The order has been removed!', 'success')
    return redirect(url_for('goToCart'))

# Renders Order History Page
@app.route('/OrderHistory')
@login_required
def OrderHistory():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if(isinstance(user, User)):
        transactions=Transaction.query.filter_by(userID=user.id, paid=True).all()
        transactions.reverse()
        setoforders=[]
        for transaction in transactions:
            orders=Order.query.filter_by(transactionID=transaction.id).all()
            setoforders.append(orders)
        size=len(transactions)
        return render_template('OrderHistory.html',title='Order History', setoforders=setoforders,transactions=transactions, size=size)
    elif isinstance(user, Restaurant) :
        transactions = Transaction.query.filter_by(restaurantID=user.id, paid=True).all()
        transactions.reverse()
        setoforders=[]
        for transaction in transactions:
            orders = Order.query.filter_by(transactionID=transaction.id).all()
            setoforders.append(orders)
        size=len(transactions)
        return render_template('OrderHistory.html',title='Order history',size=size,setoforders=setoforders,transactions=transactions)
    else :
        return render_template('home.html')


# Function for placing order
@app.route("/place_order", methods=['POST'])
@login_required
def place_order():
    data = request.json
    payment_method = data.get('payment_method')
    delivery_charge=data.get('delivery_charge')
    discounted_amount=data.get('discounted_amount')
    user_id = current_user.id
    review=data.get('review')
    transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
    if not transaction:
        return jsonify({'success': False, 'message': 'No active transaction found.'}), 404
    check=True
    for order in transaction.orders:
        if order.quantity>order.dish.quantityAvailable:
            check=False
    if check==False:
        return jsonify({'success': True,'message':"not enough quantity in stock",'check':check})
    transaction.paymentMethod = payment_method
    transaction.amount = discounted_amount
    transaction.deliveryCharge=delivery_charge
    transaction.deliveryLatitude=current_user.latitude
    transaction.deliveryLongitude=current_user.longitude
    transaction.review = review
    for order in transaction.orders:
        order.dish.quantityAvailable-=order.quantity
    if(payment_method=='cash'):
        transaction.paid = True
    transaction.date = datetime.now()
    db.session.commit()
    return jsonify({'success': True, 'total_price': discounted_amount,'check':check}), 200
 


# Function for calculating distance between two locations on a map
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # Calculate the change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Calculate the distance using Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    
    return distance


# Function for making payments
@app.route('/payment/<int:amount>',methods=['GET','POST'])
@login_required
def Payment(amount):
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    if amount==0:
        flash('Your cart is empty')
        return redirect(url_for('goToCart'))
    return render_template('Payment.html',price= amount)

@app.route('/success',methods=['POST','GET'])
@login_required
def Success():
    if(current_user.is_authenticated and current_user.id==1):
        return redirect(url_for('admin'))
    user = current_user
    if isinstance(user, User):
        transactions = Transaction.query.filter_by(userID=user.id, paid=False).all()
        for t in transactions:
            t.paid = True
        db.session.commit()
    return render_template('Success.html')


