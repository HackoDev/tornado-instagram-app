from concurrent.futures import ThreadPoolExecutor

import bcrypt
import tornado.gen
from tornado.process import cpu_count

pool = ThreadPoolExecutor(cpu_count())


@tornado.gen.coroutine
def make_password(password: str):
    return (
        yield pool.submit(
            bcrypt.hashpw,
            password.encode(),
            bcrypt.gensalt()
        )
    )


@tornado.gen.coroutine
def check_password(password: str, hashed_password: str):
    _hashed_password = yield pool.submit(
        bcrypt.hashpw,
        password.encode(),
        hashed_password.encode()
    )
    return _hashed_password == hashed_password.encode()
