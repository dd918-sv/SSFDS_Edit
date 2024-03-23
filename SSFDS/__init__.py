from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///site.db'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfqZKEpAAAAABXmGAAsW6LwcsmYi59vm-I5H5HW'  # Replace with your reCAPTCHA public key
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfqZKEpAAAAADPr646iwLraCTpcHSV_pUJkMYXF'  # Replace with your reCAPTCHA private key
app.config['RECAPTCHA_USE_SSL'] = False
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'priorityencoder@gmail.com'
app.config['MAIL_PASSWORD'] = 'dqvu ajqc shgn qyln'

mail=Mail(app)

from SSFDS import routes