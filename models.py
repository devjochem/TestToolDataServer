import json

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import Text, JSON
from werkzeug.security import generate_password_hash, check_password_hash

from utils import generate_api_key

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key_hash = db.Column(db.String(128), unique=True, nullable=False)
    api_data = db.relationship('APIData', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_api_key(self, api_key):
        self.api_key_hash = generate_password_hash(api_key)

    def check_api_key(self, api_key):
        return check_password_hash(self.api_key_hash, api_key)


class APIData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    serial_number = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='data_entries')