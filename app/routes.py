from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required


from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
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


@app.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title='Register')


@app.route('/user_profile/<username>')
@login_required
def user_profile(username):
    """View function to display user profiles"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} does not exist.'.format(username))
        return redirect(url_for('index'))

    return render_template('user_profile.html', user=user, title='Profile')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """View function to edit user profiles"""

    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Your profile has been updated successfully!')
        return redirect(url_for('user_profile', username=current_user.username))

    return render_template('edit_profile.html', form=form, title='Edit Profile')


@app.before_request
def before_request():
    """Actions to take before each request"""

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
