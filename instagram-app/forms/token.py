from wtforms import Form
from wtforms import validators
from wtforms.fields import SelectField
from wtforms.fields import StringField
from wtforms.fields import PasswordField


class TokenForm(Form):
    """
    Token registration form.
    Would be used for validation request data from user.
    """

    # available choices for platform
    PLATFORM_CHOICES = (
        ('web', 'Web'),
        ('ios', 'iOS'),
        ('android', 'android'),
        ('win_phone', 'Windows Phone'),
    )

    platform = SelectField(choices=PLATFORM_CHOICES)
    client_info = StringField(validators=[
        validators.Length(min=5, max=512),
        validators.DataRequired()
    ])
