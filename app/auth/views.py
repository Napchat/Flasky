from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user

from . import auth
from ..models import User, db, Role
from .forms import LoginForm, RegistrationForm, UpdatePasswordForm, PasswordResetRequestForm, PasswordResetForm
from ..email import send_email

@auth.before_app_first_request
def before_first_request():
    Role.insert_roles()

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
        current_user.ping()
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # this method is invoked to record the user as logged in for the user session.
            # it takes the user to log in and an optional 'remember me' Boolean, if the boolean
            # value is False causing the user session to expire when the browser window is closed,
            # so the user will have to log in again next time. if it is True, a long-term cookie
            # to be set in the user's browser and with that the user session can be restored.
            login_user(user, form.remember_me.data)

            # if the login form was presented to the user to prevent unauthorized access to a 
            # pretected URL, then Flask_Login saved the original URL in the `next` query string
            # argument, which can be accessed from the `request.args` dict.
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        send_email(u.email, 'Confirm Your Account', 'auth/email/confirm', user=u, token=token)
        login_user(u)
        flash('We send a email to you for confirmation, please check your emailbox.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', \
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
    
@auth.route('/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('You have successfully updateded your password.')
            return redirect(url_for('main.user', username=current_user.username))
    return render_template('auth/update_password.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def password_reset_request():
    '''Notifing User to input their email and check if it is existed,
    then send a email to user with a reset token.
    '''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        session['reset_email'] = form.email.data
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password', \
                       'auth/email/reset_password', user=user, token=token, next=request.args.get('next'))
        flash('An email with instructions to reset your password has been sent to you')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=session['reset_email']).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('You have successfully reset your password.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
    