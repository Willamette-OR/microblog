from flask import render_template, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    """View function for the index page"""

    title = 'Home'
    user = 'gg'
    posts = [{'author': 'gg', 'post': 'I am here in the shadows!'},
             {'author': 'pp', 'post': 'xixi'}]

    return render_template('index.html', title=title, user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """View function for the login page"""

    form = LoginForm()

    if form.validate_on_submit():
        return redirect(url_for('index'))

    return render_template('login.html', form=form)
