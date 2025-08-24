import json
import secrets
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from werkzeug.security import generate_password_hash

from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE
from models import db, User, APIData
from routes import register_routes
from utils import generate_api_key, get_serial_from_content
import os
from config import MASTER_API_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def ensure_master_api_key():
    """Generate and persist master API key if missing."""
    if not MASTER_API_KEY:
        new_key = secrets.token_hex(32)  # Strong 64-char key
        config_path = os.path.join(os.path.dirname(__file__), "config.py")

        # Read existing config
        with open(config_path, "r") as f:
            config_lines = f.readlines()

        # Replace MASTER_API_KEY line
        with open(config_path, "w") as f:
            for line in config_lines:
                if line.strip().startswith("MASTER_API_KEY"):
                    f.write(f'MASTER_API_KEY = "{new_key}"\n')
                else:
                    f.write(line)

        print(f"[INFO] Master API Key generated and saved to config.py: {new_key}")
        return new_key
    return MASTER_API_KEY

MASTER_API_KEY = ensure_master_api_key()

db.init_app(app)

register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)