import json
from http import HTTPStatus

import tornado.gen
from bson import json_util
from handlers import mixins


class UserSessionsHandler(mixins.JsonRequestHandler,
                          mixins.LimitOffsetMixin,
                          mixins.AuthTokenRequiredMixin):

    default_errors = {
        'unauthorized': 'You don\'t authorized'
    }

    @tornado.gen.coroutine
    def get(self):
        limit, offset = self.get_page_data()
        items = []
        if self.request.auth_token.get('user', None):
            cursor = self.settings['db'].tokens.find({
                'user': self.request.auth_token.get('user')
            }, {
                'key': 1, 'platform': 1, '_id': 0, 'client_info': 1
            }).limit(limit).skip(offset)

            while (yield cursor.fetch_next):
                obj = cursor.next_object()
                items.append(obj)
            self.write(json.dumps(items, default=json_util.default))
            return None

        self.write_error(
            HTTPStatus.UNAUTHORIZED,
            message=self.default_errors['unauthorized']
        )
