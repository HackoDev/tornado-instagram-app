from http import HTTPStatus

import utils.auth
import tornado.gen
from handlers import mixins
from forms.login import LoginForm


class LoginHandler(mixins.JsonRequestHandler, mixins.AuthTokenRequiredMixin):

    INVALID_CREDENTIALS = 'Invalid username/password pair'

    @tornado.gen.coroutine
    def post(self):
        if self.request.auth_token.get('user', None):
            self.write({
                'detail': 'You are already logged'
            })
            return None

        self.is_valid_json(raise_exception=True)
        form = LoginForm(data=self.get_json_data())
        if not form.validate():
            self.write_error(
                HTTPStatus.BAD_REQUEST,
                message=self.INVALID_CREDENTIALS
            )
            return None

        credentials = form.data
        user = yield self.settings['db'].users.find_one(
            {'username': credentials['username']}
        )

        if not user:
            self.write_error(
                HTTPStatus.UNAUTHORIZED,
                message=self.INVALID_CREDENTIALS
            )
            return None

        if (yield utils.auth.check_password(
            credentials['password'],
            user['password'].decode()
        )):
            yield self.settings['db'].tokens.update({
                'key': self.request.auth_token['key'],
            }, {
                '$set': {
                    'user': user['_id']
                }
            })
            self.write({
                'detail': 'You successfully logged'
            })
        else:
            self.write_error(
                HTTPStatus.UNAUTHORIZED,
                message=self.INVALID_CREDENTIALS
            )
