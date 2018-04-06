from flask import render_template, redirect, url_for, flash
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

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(form.password.data):
            flash('You have logged in successfully!')
            return redirect(url_for('index'))

        flash('Invalid username or password. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)
