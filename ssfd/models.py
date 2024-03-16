from ssfd import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='restaurant.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_open=db.column(db.Boolean, nullable=False, default=False)
    latitude = db.Column(db.Decimal(9, 6), nullable=True)
    longitude = db.Column(db.Decimal(9, 6), nullable=True)
    content = db.Column(db.Text, nullable=False)
    dishes = db.relationship('Dish', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restaurant('{self.username}', '{self.email}', '{self.image_file}')"
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='user.jpg')
    latitude = db.Column(db.Decimal(9, 6), nullable=True)
    longitude = db.Column(db.Decimal(9, 6), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.Enum('user', 'ngo'), nullable=False, default='user')
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}, '{self.user_type}')"

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    restaurant = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    def __repr__(self):
        return f"Dish('{self.name}', '{self.price}', '{self.description}', '{self.image}')"

class Transaction(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_items = db.relationship('OrderItem', backref='transaction')
    order_placed = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f"UserTransaction(id={self.id}, user_id={self.user_id})"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('user_transaction.id'), nullable=False)  
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"OrderItem(id={self.id}, transaction_id={self.transaction_id}, dish_id={self.dish_id}, quantity={self.quantity})"

