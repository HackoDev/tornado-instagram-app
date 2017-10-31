import motor
import tornado.web
import tornado.ioloop

from handlers.login import LoginHandler
from handlers.logout import LogoutHandler
from handlers.handshake import HandshakeHandler
from handlers.user_detail import UserDetailHandler
from handlers.registration import RegistrationHandler
from handlers.user_sessions import UserSessionsHandler
from handlers.instagram_auth import InstagramAuthHandler


def make_app():
    client = motor.MotorClient()
    url_handlers = [
        tornado.web.URLSpec(r"^/api/handshake$", HandshakeHandler,
                            name="handshake"),
        tornado.web.URLSpec(r"^/api/login$", LoginHandler, name="login"),
        tornado.web.URLSpec(r"^/api/logout$", LogoutHandler, name="logout"),
        tornado.web.URLSpec(r"^/api/registration$", RegistrationHandler,
                            name="registration"),
        tornado.web.URLSpec(r"^/api/me$", UserDetailHandler, name="me-info"),
        tornado.web.URLSpec(r"^/api/me/sessions$", UserSessionsHandler,
                            name="me-sessions"),
        tornado.web.URLSpec(r"^/api/instagram_auth/$", InstagramAuthHandler,
                            name="instagram-auth")
    ]
    return tornado.web.Application(
        handlers=url_handlers,
        debug=True,
        autoreload=True,
        db=client.test,
        page_size=10,
        auth_header_name='X-Authorization',
        instagram_config={
            'credentials': (
                'c601592a3b13456a94fbd66d44e97a7a',
                '8e9828a8001842f1b7392616915ff101'
            ),
            'redirect_uri': 'http://localhost:8888/instagram_auth/'
        }
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running on {port} port".format(port=8888))
    tornado.ioloop.IOLoop.current().start()
