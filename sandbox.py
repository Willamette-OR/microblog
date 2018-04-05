from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    """Create shell contexts for app and db testing"""

    return {'db': db, 'User': User, 'Post': Post}
