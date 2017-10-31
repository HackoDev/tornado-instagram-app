import tornado.gen
from views import mixins


class LogoutHandler(mixins.JsonRequestHandler,
                        mixins.AuthTokenRequiredMixin):

    @tornado.gen.coroutine
    def post(self):
        if self.request.auth_token.get('user', None):
            yield self.settings['db'].tokens.update({
                'key': self.request.auth_token.get('key')
            }, {
                '$set': {
                    'user': None
                }
            })
        self.write({
            'detail': 'You successfully logout'
        })
