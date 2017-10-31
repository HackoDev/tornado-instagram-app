import datetime
import exceptions
from http import HTTPStatus
from concurrent.futures import ThreadPoolExecutor

import tornado.gen
from handlers import mixins
from instagram import client
from tornado.process import cpu_count
from instagram.oauth2 import OAuth2AuthExchangeError

pool = ThreadPoolExecutor(cpu_count())


class InstagramAuthHandler(mixins.JsonRequestHandler,
                           mixins.AuthTokenRequiredMixin):

    INVALID_CREDENTIALS = 'Invalid username/password pair'

    @tornado.gen.coroutine
    def get(self):

        credentials = dict(zip(
            ('client_id', 'client_secret'),
            self.settings['instagram_config']['credentials']
        ))
        uri = 'http://{hostname}{path}?auth_token={auth_token}'.format(
            hostname=self.request.headers.get('Host'),
            path=self.reverse_url('instagram-auth'),
            auth_token=self.request.auth_token['key']
        )
        i_client = client.InstagramAPI(**credentials, redirect_uri=uri)

        code = self.get_argument('code', None, True)
        if code:
            try:
                access_token, inst_profile = yield pool.submit(
                    i_client.exchange_code_for_access_token, code)
            except OAuth2AuthExchangeError as e:
                raise exceptions.APIHTTPError(
                    status_code=400,
                    reason={'detail': str(e)}
                )
            inst_profile.setdefault('access_token', access_token)
            current_user = self.request.auth_token.get('user', None)

            user_relation = yield self.settings['db'].users.find_one({
                'accounts.username': inst_profile['username']
            })
            session = self.request.auth_token

            if current_user:
                # check user relation with account
                if user_relation and user_relation['_id'] != current_user:
                    self.write_error(
                        HTTPStatus.BAD_REQUEST,
                        message='Account already linked with another user'
                    )
                else:
                    if not user_relation:
                        yield self.settings['db'].users.update(
                            {'_id': current_user},
                            {'$addToSet': {'accounts': inst_profile}}
                        )
                    self.write({
                        'detail': 'You successfully logged'
                    })
            else:
                if user_relation:

                    yield self.settings['db'].users.update({
                        'accounts.username': inst_profile['username']},
                        {'$set': {
                            'accounts.$': inst_profile
                        }}
                    )
                    yield self.settings['db'].tokens.update({
                        'key': session['key']
                    }, {
                        '$set': {
                            'user': user_relation['_id']
                        }}
                    )
                else:
                    inserted = yield self.settings['db'].users.insert_one({
                        'username': inst_profile['username'],
                        'accounts': [inst_profile],
                        'joined_at': datetime.datetime.utcnow()
                    }, {
                        'writeConcern': {'w': 'majority', 'wtimeout': 100}
                    })
                    yield self.settings['db'].tokens.update({
                        'key': session['key']
                    }, {'$set': {
                        'user': inserted.inserted_id}}
                    )
                self.write({
                    'detail': 'You successfully logged'
                })
        else:
            self.write({
                'login_url': i_client.get_authorize_url()
            })
