import json

from flask import Blueprint, session, redirect, url_for, request, render_template, flash

from models import db, User, APIData
from routes.base import login_required
from utils import get_serial_from_content, generate_api_key

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

'''
        USER DASHBOARDS AND FUNCTIONS
'''


@admin_dashboard_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname and pwd:
            new_user = User(username=uname)
            new_user.set_password(pwd)
            api_key = generate_api_key()
            db.session.add(new_user)
            db.session.commit()
            flash(f'New user created with API key: {api_key}', 'success')

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@admin_dashboard_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        if uname and pwd:
            new_user = User(username=uname)
            new_user.set_password(pwd)
            api_key = generate_api_key()
            db.session.add(new_user)
            db.session.commit()
            flash(f'New user created with API key: {api_key}', 'success')

    return render_template('create_user.html')

@admin_dashboard_bp.route('/admin/user/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_user_info(user_id):
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    return render_template('user_info.html', user_id=user_id)

@admin_dashboard_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard.admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

@admin_dashboard_bp.route('/admin/user/<int:user_id>/regen_api', methods=['POST'])
@login_required
def admin_regen_api_key(user_id):
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard.admin_dashboard'))

    from utils import generate_api_key
    new_api_key = generate_api_key()
    user.set_api_key(new_api_key)
    db.session.commit()
    flash(f"New API Key for {user.username}: {new_api_key}", "success")

    return redirect(url_for('admin_dashboard'))

@admin_dashboard_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard.admin_dashboard'))

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        regen_api = request.form.get('regen_api')

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)
        if regen_api:
            from utils import generate_api_key
            new_api_key = generate_api_key()
            session['api_key'] = new_api_key  # just for visibility
            flash(f"New API Key: {new_api_key}", "success")

        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_dashboard.admin_dashboard'))

    return render_template("admin_edit_user.html", user=user)
