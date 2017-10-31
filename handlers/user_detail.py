import json
from http import HTTPStatus

import tornado.gen
from bson import json_util
from handlers import mixins


class UserDetailHandler(mixins.JsonRequestHandler,
                        mixins.AuthTokenRequiredMixin):

    default_errors = {
        'unauthorized': 'You don\'t authorized'
    }

    @tornado.gen.coroutine
    def get(self):
        if self.request.auth_token.get('user', None):
            user = yield self.settings['db'].users.find_one({
                '_id': self.request.auth_token.get('user')
            }, {
                'username': 1, '_id': 0
            })
            self.write(json.dumps(user, default=json_util.default))
        else:
            self.write_error(
                HTTPStatus.UNAUTHORIZED,
                message=self.default_errors['unauthorized']
            )
