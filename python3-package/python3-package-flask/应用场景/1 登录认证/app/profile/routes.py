# app/profile/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User
from .. import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    print(f"Current user: {current_user}")  # 调试信息
    print(f"User authenticated: {current_user.is_authenticated}")  # 调试信息

    if request.method == 'POST':
        # 更新用户信息
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.bio = request.form['bio']

        db.session.commit()

        flash('资料更新成功', 'success')
        return redirect(url_for('profile.view_profile'))


    # 获取用户信息
    user = User.query.get(current_user.id)
    print(f"User: {user}")
    print(f"User's first name: {user.first_name}")
    print(f"User's last name: {user.last_name}")
    print(f"User's bio: {user.bio}")

    return render_template('profile.html', user=current_user)
