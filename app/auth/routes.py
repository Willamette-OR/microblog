from flask import render_template, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user


from app import app, db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    RequestPasswordResetForm, PasswordResetForm
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """View function for the login page"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('You have logged in successfully!')
            return redirect(url_for('index'))

        flash('Invalid username or password. Please try again.')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/logout')
def logout():
    """View function for user logout"""

    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """View function to register new users"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('You have registered successfully! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Register')


@bp.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    """View function for user password reset requests"""

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user, recipients=[user.email],
                                      sender=app.config['ADMINS'][0])
        flash('Please check your email for a link to reset your password!')
        return redirect(url_for('auth.login'))

    return render_template('auth/request_password_reset.html', form=form,
                           title='Request Password Reset')


@bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """View function to reset user passwords if the token is valid"""

    user = User.verify_password_reset_token(token)
    if not user:
        flash('Invalid link for password reset. '
              'Please double check your email and try again.')
        return redirect(url_for('auth.login'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfully reset. Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('auth/password_reset.html', form=form,
                           title='Reset Password')
