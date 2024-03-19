from SSFDS import db, login_manager,app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime, timedelta

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
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    open=db.Column(db.Boolean)
    address = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Double, nullable=True)
    longitude = db.Column(db.Double, nullable=True)
    content = db.Column(db.Text, nullable=True)
    dishes = db.relationship('Dish', backref='restaurant', lazy=True)
    transaction = db.relationship('Transaction', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restaurant('{self.username}', '{self.email}', '{self.image}')"
    
    def get_token(self, expires_sec=300):
        serial = Serializer(app.config['SECRET_KEY'])
        expires_at = datetime.now() + timedelta(seconds=expires_sec)
        return serial.dumps({'user_id': self.id, 'exp': expires_at.isoformat()})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            data = serial.loads(token)
            expires_at = datetime.fromisoformat(data.get('exp'))
            if datetime.now() <= expires_at:
                user_id = data['user_id']
                return Restaurant.query.get(user_id)
        except:
            pass
        return None

    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    address = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Double, nullable=True)
    longitude = db.Column(db.Double, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    ngo = db.Column(db.Boolean)
    transaction = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}, '{self.ngo}')"
    
    def get_token(self,expires_sec=300):
        serial=Serializer(app.config['SECRET_KEY'])
        expires_at = datetime.now() + timedelta(seconds=expires_sec)
        return serial.dumps({'user_id': self.id, 'exp': expires_at.isoformat()})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            data = serial.loads(token)
            expires_at = datetime.fromisoformat(data.get('exp'))
            if datetime.now() <= expires_at:
                user_id = data['user_id']
                return User.query.get(user_id)
        except:
            pass
        return None

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    order = db.relationship('Order', backref='dish', lazy=True)

    def __repr__(self):
        return f"Dish('{self.name}', '{self.price}', '{self.description}', '{self.image}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False, default=0)
    orders = db.relationship('Order', backref='transaction', lazy=True)
    orderplaced = db.Column(db.Boolean)
    paymentMethod = db.Column(db.String(20), nullable=False)
    paid = db.Column(db.Boolean)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dishID = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transactionID = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)