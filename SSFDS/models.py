from SSFDS import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def loadUser(userId):
    user=User.query.get(int(userId))
    restaurant=Restaurant.query.get(int(userId))
    if(user):
        return user
    else: 
        return restaurant

# @login_manager.user_loader
# def loadRestaurant(restaurantId):
#     return Restaurant.query.get(int(restaurantId))

class Restaurant(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='restaurant.jpg')
    password = db.Column(db.String(60), nullable=False)
    open=db.Column(db.Boolean)
    address = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Double, nullable=True)
    longitude = db.Column(db.Double, nullable=True)
    content = db.Column(db.Text, nullable=True)
    dishes = db.relationship('Dish', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restaurant('{self.username}', '{self.email}', '{self.image}')"
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='user.jpg')
    address = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Double, nullable=True)
    longitude = db.Column(db.Double, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    ngo = db.Column(db.Boolean)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}, '{self.ngo}')"

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    def __repr__(self):
        return f"Dish('{self.name}', '{self.price}', '{self.description}', '{self.image}')"
