from datetime import datetime, timedelta
from blogweb import db, login_manager
from flask_login import UserMixin
from blogweb import app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Posting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default='Untitled Post')
    content = db.Column(db.Text, nullable=False, default='')
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_edited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_published}')"

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posting.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    about = db.Column(db.Text, unique=True, nullable=False, default='')
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Posting', backref='author', lazy=True)
    comments = db.relationship('Comments', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"