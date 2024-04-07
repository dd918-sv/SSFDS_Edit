from SSFDS import db, app, bcrypt
from SSFDS.models import User

with app.app_context():
    db.drop_all()
    db.create_all()
    hashedPassword=bcrypt.generate_password_hash("password").decode('utf-8')
    user = User(id= 1, username="admin", email="admin@gmail.com", password=hashedPassword, address="admin address", ngo=False)
    db.session.add(user)
    db.session.commit()



