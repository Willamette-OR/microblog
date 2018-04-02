from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    """View function for the index page"""

    title = 'Home'
    user = 'gg'
    posts = [{'author': 'gg', 'post': 'I am here in the shadows!'},
             {'author': 'pp', 'post': 'xixi'}]

    return render_template('index.html', title=title, user=user, posts=posts)
