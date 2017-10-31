import motor
import handlers
import tornado.web
import tornado.ioloop


def make_app():
    client = motor.MotorClient()
    url_handlers = [
        tornado.web.URLSpec(r"^/api/handshake$", handlers.HandshakeHandler,
                            name="handshake"),
        tornado.web.URLSpec(r"^/api/login$", handlers.LoginHandler,
                            name="login"),
        tornado.web.URLSpec(r"^/api/logout$", handlers.LogoutHandler,
                            name="logout"),
        tornado.web.URLSpec(r"^/api/registration$",
                            handlers.RegistrationHandler,
                            name="registration"),
        tornado.web.URLSpec(r"^/api/me$", handlers.UserDetailHandler,
                            name="me-info"),
        tornado.web.URLSpec(r"^/api/me/sessions$",
                            handlers.UserSessionsHandler, name="me-sessions"),
        tornado.web.URLSpec(r"^/api/instagram_auth/$",
                            handlers.InstagramAuthHandler,
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
