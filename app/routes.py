from app import app


@app.route('/')
@app.route('/index')
def index():
    """View function for the index page"""

    return 'Hello World!'
