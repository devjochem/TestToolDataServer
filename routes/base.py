import json
from functools import wraps

from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from models import User

app_bp = Blueprint("app", __name__)

'''
        USER DASHBOARDS AND FUNCTIONS
'''


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id') and not session.get('admin'):
            return redirect(url_for('app.login'))
        return f(*args, **kwargs)
    return decorated
# ---------- Routes ----------
@app_bp.route('/')
def index():
    return redirect(url_for('app.login'))

@app_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        if uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard.admin_dashboard'))

        user = User.query.filter_by(username=uname).first()
        if user and user.check_password(pwd):
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard.user_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('app.login'))
    return render_template('login.html')


@app_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('app.login'))