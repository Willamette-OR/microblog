from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import lazy_gettext as _l


from app.models import User


class EditProfileForm(FlaskForm):
    """A class for the user profile editing form"""

    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About Me", validators=[DataRequired(),
                                                     Length(min=1, max=256)])
    submit = SubmitField("Submit")

    def __init__(self, original_user):
        """Save the original user object when initializing the instance"""

        super().__init__()
        self.original_user = original_user

    def validate_username(self, username):
        """Raise if the new username of the current user has already been
        taken"""

        if username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    """A class for making new posts on the index page"""

    post = TextAreaField(_l('Say something'), validators=[Length(min=1,
                                                                 max=140)])
    submit = SubmitField(_l('Submit'))
