from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '0d328c982f05063913189585f3a4489c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogweb.db'
app.config['SQLALCHEMY_BINDS'] = {'search': 'sqlite:///search.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from blogweb import routes
