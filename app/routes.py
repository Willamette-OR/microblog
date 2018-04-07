from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app import app
from app.forms import LoginForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    """View function for the index page"""

    user = 'gg'
    posts = [{'author': 'gg', 'post': 'I am here in the shadows!'},
             {'author': 'pp', 'post': 'xixi'}]

    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    """View function for user logout"""

    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))
