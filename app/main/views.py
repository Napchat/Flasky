from . import main
from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from ..models import User

@main.route('/')
@main.route('/index')
def index():
    return render_template('main/index.html')

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s is not found.' % username)
        return redirect(url_for('main.index'))
    return render_template('main/user.html', user=user)