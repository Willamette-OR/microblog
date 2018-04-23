from flask import render_template
from app import db
from app.errors import bp


@bp.errorhandler(404)
def error_not_found(error):
    """An error handler to be registered for files not found errors"""

    return render_template('errors/error_404.html'), 404


@bp.errorhandler(500)
def error_internal(error):
    """An error handler to be registered for internal errors"""

    db.session.rollback()
    return render_template('errors/error_500.html'), 500
