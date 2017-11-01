from concurrent.futures import ThreadPoolExecutor

import tornado.gen
from handlers import mixins
from tornado.process import cpu_count

pool = ThreadPoolExecutor(cpu_count())


class UserSearchHandler(mixins.JsonRequestHandler,
                        mixins.LimitOffsetMixin,
                        mixins.AuthTokenRequiredMixin):

    default_errors = {
        'unauthorized': 'You don\'t authorized'
    }

    @tornado.gen.coroutine
    def get(self):
        limit, offset = self.get_page_data()
        client = self.application.get_instagram_client(
            access_token=self.request.auth_token['session']['access_token']
        )
        users = yield pool.submit(client.user_search,
                                  q=self.get_argument('q', '', strip=True),
                                  count=limit)
        self.write({
            'results': [
                {"is_business": user.is_business, "username": user.username,
                 "profile_picture": user.profile_picture,
                 "id": user.id, "website": user.website, "bio": user.bio,
                 "full_name": user.full_name}
                for user in users
            ]
        })
