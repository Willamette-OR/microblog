from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    """View function for the index page"""

    return render_template('index.html')
