from wtforms import Form
from wtforms.fields import IntegerField


class LimitOffsetForm(Form):

    offset = IntegerField()
    limit = IntegerField()
