from flask import render_template
from app import app, db


@app.errorhandler(404)
def error_not_found(error):
    """An error handler to be registered for files not found errors"""

    return render_template('error_404.html'), 404


@app.errorhandler(500)
def error_internal(error):
    """An error handler to be registered for internal errors"""

    db.session.rollback()
    return render_template('error_500.html'), 500
