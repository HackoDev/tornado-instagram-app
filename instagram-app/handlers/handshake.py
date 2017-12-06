import uuid
import datetime
from http import HTTPStatus

import tornado.gen
from handlers import mixins
from forms.token import TokenForm


class HandshakeHandler(mixins.JsonRequestHandler,
                       mixins.AuthTokenRequiredMixin):

    REQUIRED = False

    def data_received(self, chunk):
        pass

    @tornado.gen.coroutine
    def post(self):
        if self.request.auth_token:
            self.write({
                'token': self.request.auth_token['key']
            })
            return
        self.is_valid_json(raise_exception=True)

        form = TokenForm(data=self.get_json_data())
        if not form.validate():
            self.write_error(HTTPStatus.BAD_REQUEST, message=form.errors)
            return None

        token_info = form.data
        token_info.update({
            'key': str(uuid.uuid4().hex),
            'created': datetime.datetime.utcnow()
        })
        yield self.settings['db'].tokens.insert_one(token_info)
        self.write({
            'token': token_info['key']
        })
