from http import HTTPStatus

import tornado.gen
from handlers import mixins


class SelectAccountHandler(mixins.JsonRequestHandler,
                           mixins.AuthTokenRequiredMixin):

    default_errors = {
        'unauthorized': 'You don\'t authorized',
        'bad_account': 'Incorrect username',
    }

    @tornado.gen.coroutine
    def get(self):
        auth_token = self.request.auth_token
        if not auth_token.get('user', None):
            self.write_error(
                HTTPStatus.UNAUTHORIZED,
                message=self.default_errors['unauthorized']
            )
        username = self.get_argument('username', None, True)
        if not username:
            self.write_error(
                HTTPStatus.BAD_REQUEST,
                message=self.default_errors['bad_account']
            )
        elif auth_token.get('session') and \
            auth_token['session']['username'] == username:
            self.write({
                'detail': 'You already using this account'
            })
        else:
            user = yield \
                self.settings['db'].users.find_one({'_id': auth_token['user']})
            for item in user['accounts']:
                if item['username'] == username:
                    yield self.settings['db'].tokens.update({
                        'key': auth_token['key']
                    }, {
                        '$set': {
                            'session': item
                        }
                    })
                    break
            else:
                self.write_error(
                    HTTPStatus.BAD_REQUEST,
                    message=self.default_errors['bad_account']
                )
            self.write({
                'detail': 'Account successfully switched'
            })
