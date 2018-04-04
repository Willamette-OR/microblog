from flask import render_template, redirect, url_for, flash
from app import app
from app.forms import LoginForm


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
        flash('Login requested for user {0}, remember_me = {1}'.
              format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))

    return render_template('login.html', title='Login', form=form)
