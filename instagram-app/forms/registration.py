from wtforms import Form
from wtforms import validators
from wtforms.fields import StringField
from wtforms.fields import PasswordField


class RegistrationForm(Form):

    username = StringField(validators=[
        validators.DataRequired(), validators.Email()
    ])
    password = PasswordField(validators=[
        validators.DataRequired(),
        validators.Length(min=4)
    ])
