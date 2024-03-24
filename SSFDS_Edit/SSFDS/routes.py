import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from SSFDS import app, db, bcrypt, mail
from SSFDS.forms import RestaurantRegistrationForm, UserRegistrationForm, LoginForm, UpdateForm, AddDishForm, ForgotPasswordForm, ResetPasswordForm, DonationForm
from SSFDS.models import Restaurant, User, Dish, Transaction, Order, Donation
from flask_login import login_user, current_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message


def identity():
    return len(User.query.all())+len(Restaurant.query.all())+1

@app.route("/")
@app.route("/home")
def home():
    user=current_user
    if(user.is_authenticated and (user.latitude is None or user.longitude is None)):
        flash('Please enter your location first in Account settings for getting list of restaurants','warning')
        return redirect(url_for('account'))
    return render_template('home.html', restaurants=Restaurant.query.all(),title='Home',calculate_distance=calculate_distance)

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
        user = User(id= identity(), username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data, ngo=form.ngo.data)
        db.session.add(user)
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

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

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

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
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

#edited
@app.route("/addDish", methods=['GET', 'POST'])
@login_required
def addDish():
    if current_user.latitude is None or current_user.longitude is None:
        print('Location not entered.')
        flash('Please enter your location first in Account settings','warning')
        return redirect(url_for('account'))
    form=AddDishForm()
    if form.validate_on_submit():
        dish=Dish(name=form.name.data,price=form.price.data,description=form.description.data,restaurant=current_user)
        if form.picture.data:
            pictureFile = save_picture(form.picture.data, 'static/dish_pics')
            dish.image = pictureFile
        db.session.add(dish)
        db.session.commit()
        flash('Dish added successfully','success')
        return redirect(url_for('account'))
    return render_template('/addDish.html',form=form)

@app.route("/delete-dish/<int:restaurant_id>/<int:dish_id>", methods=['DELETE'])
def delete_dish(restaurant_id, dish_id):
    dish = Dish.query.filter_by(id=dish_id, restaurantID=restaurant_id).first_or_404()
    if dish:
        db.session.delete(dish)
        db.session.commit()
        flash('The dish has been deleted!', 'success')
        return jsonify({'redirect_url': url_for('account')}), 200
    
def sendMail(user):
    token=user.get_token()
    msg=Message('Password Reset Request',recipients=[user.email],sender='priorityencoder@gmail.com')
    msg.body=f'''To reset your password, visit the following link:
    {url_for('reset_token',token=token,_external=True)}
    '''
    mail.send(msg)

@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
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
        

@app.route('/DonationsReceived')
@login_required
def DonationsReceived():
    user = current_user
    if(isinstance(user, User) and current_user.ngo==True):
        donations=Donation.query.filter_by(ngoID=current_user.id).all()
        return render_template('DonationsReceived.html',title='Donations Received',donations=donations)
    else:
        return redirect(url_for('home'))

@app.route('/DonationsGiven')
@login_required
def DonationsGiven():
    user = current_user
    if(isinstance(user, User) and current_user.ngo==False):
        donations=Donation.query.filter_by(userID=current_user.id).all()
        return render_template('DonationsGiven.html',title='Donations Given',donations=donations)
    else:
        return redirect(url_for('home'))
    
@app.route('/Donate')
@login_required
def Donate():
    user = current_user
    if(isinstance(user, User) and current_user.ngo==False):
        ngos=User.query.filter_by(ngo=True).all()
        return render_template('Donate.html',title='Donate', ngos=ngos)
    else:
        return redirect(url_for('home'))

@app.route('/Donate/<int:ngo_ID>', methods=['GET', 'POST'])
@login_required
def DonateToNGO(ngo_ID):
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

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/location', methods=['POST'])
def location():
    lat = request.form['lat']
    lng = request.form['lng']
    current_user.latitude = lat
    current_user.longitude = lng
    db.session.commit()
    return render_template('location_saved.html', lat=lat, lng=lng)

@app.route("/menu/<int:restaurant_id>")
@login_required
def menu(restaurant_id):
    if(isinstance(current_user,Restaurant)):
        return redirect(url_for('home'))
    elif current_user.latitude is None or current_user.longitude is None:
        flash('Please enter your location first in Account settings','warning')
        return redirect(url_for('home'))
    restaurant=Restaurant.query.get(restaurant_id)
    dishes=Dish.query.filter_by(restaurantID=restaurant_id).all()
    return render_template('menu.html',restaurant=restaurant,dishes=dishes)


@app.route("/addToCart/<int:restaurant_id>/<int:user_id>/<int:dish_id>", methods=['POST', 'GET'])
@login_required
def addToCart(restaurant_id, user_id, dish_id):
    if isinstance(current_user, Restaurant):
        flash('A restaurant is not allowed to order!', 'warning')
        return redirect(url_for('home'))

    transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
    
    if transaction is None:
        transaction = Transaction(userID=user_id, restaurantID=restaurant_id, paymentMethod='cash', paid=False, orderplaced=False, discount=0)
        if current_user.ngo:
            transaction.discount = 40
        else:
            transaction.discount = 10
        db.session.add(transaction)
        db.session.commit()
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

    

@app.route("/goToCart", methods=['GET', 'POST'])
@login_required
def goToCart():
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
    # Fetch the price per unit for each order and store it in a list
    # prices_per_unit = [order.dish.price for order in orders]
    order=orders[0]
    restaurant=order.transaction.restaurant
    distance=calculate_distance(restaurant.latitude,restaurant.longitude,user.latitude,user.longitude)
    delivery_charge=0
    if distance>2:
        delivery_charge=5*(distance-2)
    print(distance)
    return render_template('cart.html', orders=orders,delivery_charge=delivery_charge, title='Cart')


@app.route("/remove_order/<int:order_id>", methods=['POST'])
@login_required
def remove_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash('The order has been removed!', 'success')
    return redirect(url_for('goToCart'))

@app.route('/OrderHistory')
@login_required
def OrderHistory():
    user = current_user
    if(isinstance(user, User)):
        orders = Order.query.join(Transaction).join(Restaurant).filter(Transaction.userID == user.id).all()  
        transactions=Transaction.query.all()   
        # print(orders)   
        return render_template('OrderHistory.html',title='Order History',orders=orders,transactions=transactions)
    else:
        return redirect(url_for('home'))

@app.route("/place_order", methods=['POST'])
@login_required
def place_order():
    data = request.json
    orders = data.get('orders', [])
    payment_method = data.get('payment_method')
    if not orders:
        return jsonify({'success': False, 'message': 'No orders found.'}), 400

    user_id = current_user.id
    transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
    if not transaction:
        return jsonify({'success': False, 'message': 'No active transaction found.'}), 404

    total_price = 0
    for order_data in orders:
        dish_id = order_data.get('dish_id')
        quantity = order_data.get('quantity')
        if dish_id is None or quantity is None:
            continue

        dish = Dish.query.get(dish_id)
        if not dish:
            continue

        order = Order.query.filter_by(transactionID=transaction.id, dishID=dish_id).first()
        if order:
            order.quantity = quantity
            order.transaction.date = datetime.now()
        else:
            order = Order(transactionID=transaction.id, dishID=dish_id)
            db.session.add(order)

        total_price += dish.price * quantity

    # Update the payment method
    transaction.paymentMethod = payment_method

    # Mark the transaction as paid
    transaction.paid = True
    db.session.commit()

    return jsonify({'success': True, 'total_price': total_price})

    #acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371 


from math import radians, sin, cos, sqrt, atan2

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



# @app.route("/place_order", methods=['POST'])
# @login_required
# def place_order():
#     data = request.json
#     orders = data.get('orders', [])
#     paymentMethod=data.get('payment_method')
#     if not orders:
#         return jsonify({'success': False, 'message': 'No orders found.'}), 400

#     user_id = current_user.id
#     transaction = Transaction.query.filter_by(userID=user_id, paid=False).first()
#     if not transaction:
#         return jsonify({'success': False, 'message': 'No active transaction found.'}), 404

#     total_price = 0
#     for order_data in orders:
#         dish_id = order_data.get('dish_id')
#         quantity = order_data.get('quantity')
#         if dish_id is None or quantity is None:
#             continue

#         dish = Dish.query.get(dish_id)
#         if not dish:
#             continue

#         order = Order.query.filter_by(transactionID=transaction.id, dishID=dish_id).first()
#         if order:
#             order.quantity = quantity
#             order.transaction.date=datetime.now()
#         else:
#             order = Order(transactionID=transaction.id, dishID=dish_id)
#             db.session.add(order)

#         total_price += dish.price * quantity

#     # Mark the transaction as paid
#     transaction.paid = True
#     db.session.commit()

#     return jsonify({'success': True, 'total_price': total_price})


