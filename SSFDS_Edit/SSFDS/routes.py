from flask import render_template, url_for, flash, redirect, request, jsonify
from SSFDS import app, db, bcrypt
from SSFDS.forms import RestaurantRegistrationForm, UserRegistrationForm, LoginForm, AddDishForm
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
        restaurant = Restaurant(username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data)
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
        restaurant = User(username=form.username.data, email=form.email.data, password=hashedPassword, address=form.address.data, ngo=form.ngo.data)
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
            flash('Login Successful','success') #doubtful line
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

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/addDish.html", methods=['GET', 'POST'])
@login_required
def addDish():
    form=AddDishForm()
    if form.validate_on_submit():
        dish=Dish(name=form.name.data,price=form.price.data,description=form.description.data,restaurant=current_user)
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
        print('hi')
        return jsonify({'redirect_url': url_for('account')}), 200
