import datetime
from http import HTTPStatus

import utils.auth
import tornado.gen
from handlers import mixins
from forms.registration import RegistrationForm


class RegistrationHandler(mixins.JsonRequestHandler,
                          mixins.AuthTokenRequiredMixin):

    default_errors = {
        'not_unique': 'User with "%s" username already exists'
    }

    @tornado.gen.coroutine
    def post(self):
        self.is_valid_json(raise_exception=True)
        form = RegistrationForm(data=self.get_json_data())
        if not form.validate():
            self.write_error(
                HTTPStatus.BAD_REQUEST,
                message=form.errors
            )
            return None

        username = form.data.get('username')
        user = yield self.settings['db'].users.find_one({
            'username': username
        })
        if user is not None:
            self.write_error(
                HTTPStatus.BAD_REQUEST,
                message=self.default_errors['not_unique'] % username
            )
            return None

        user_info = form.data
        hashed_password = yield utils.auth.make_password(
            user_info['password']
        )
        user_info.update({
            'password': hashed_password,
            'joined_at': datetime.datetime.utcnow()
        })
        yield self.settings['db'].users.insert_one(user_info)
        user = yield self.settings['db'].users.find_one(user_info)
        yield self.settings['db'].tokens.update({
            'key': self.request.auth_token['key'],
        }, {
            '$set': {
                'user': user['_id']
            }
        })
        self.write({
            'detail': 'You successfully registered'
        })
