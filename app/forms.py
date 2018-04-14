from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, \
    ValidationError


from app.models import User


class LoginForm(FlaskForm):
    """A class for login forms"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Submit")


class RegistrationForm(FlaskForm):
    """A class for the registration form"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat password',
                               validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate if the username has already been taken"""

        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Validate if the email address has already been taken"""

        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


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

    post = TextAreaField('Say something', validators=[Length(min=1, max=140)])
    submit = SubmitField('Submit')


class RequestPasswordResetForm(FlaskForm):
    """A class for requesting user password reset"""

    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')
