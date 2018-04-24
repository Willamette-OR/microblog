from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


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


class RequestPasswordResetForm(FlaskForm):
    """A class for requesting user password reset"""

    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')


class PasswordResetForm(FlaskForm):
    """A class for resetting user passwords"""

    password = PasswordField('Enter new password:', validators=[DataRequired()])
    password_2 = PasswordField('Repeat new password:',
                               validators=[EqualTo('password')])
    submit = SubmitField('Submit')
