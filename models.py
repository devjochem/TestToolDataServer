import json
from zoneinfo import ZoneInfo

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_data = db.relationship('APIData', backref='owner', lazy=True)
    api_keys = db.relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_api_key(self, api_key):
        return any(key.check_key(api_key) for key in self.api_keys)


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    key_hash = db.Column(db.String(128), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(ZoneInfo("Europe/Amsterdam")))
    user = db.relationship("User", back_populates="api_keys")

    def set_key(self, key):
        self.key_hash = generate_password_hash(key)

    def check_key(self, key):
        return check_password_hash(self.key_hash, key)

class APIData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    specs = db.Column(db.Text, nullable=False)
    test_results = db.Column(db.Text, nullable=False)
    serial_number = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(ZoneInfo("Europe/Amsterdam")))
    user = db.relationship('User', backref='data_entries')

class BatData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    serial_number = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(ZoneInfo("Europe/Amsterdam")))
    user = db.relationship('User', backref='bat_entries')