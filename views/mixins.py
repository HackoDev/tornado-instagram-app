import json
import traceback
import exceptions
from http import HTTPStatus

import tornado.gen
import tornado.web
from tornado.web import RequestHandler
from forms.paginator import LimitOffsetForm


class JsonRequestHandler(RequestHandler):
    """
    JSON Request handler Mixin. 
    It implements helpers methods for json types.
    """

    _incorrect_json = 'Incorrect json data'
    _cached_json_data = None
    _is_valid = None

    def data_received(self, chunk):
        pass

    def is_valid_json(self, raise_exception=False) -> bool:
        """
        Checking json body from request user.
        
        :param raise_exception: bool Use for raising exception on bad data
        :return: bool
        """
        if isinstance(self._is_valid, bool):
            return self._is_valid
        self._is_valid = self.get_json_data() is not None
        if not self._is_valid and raise_exception:
            self.write_error(
                HTTPStatus.BAD_REQUEST,
                message=self._incorrect_json
            )
        return self._is_valid

    def get_json_data(self) -> dict or None:
        """
        Parse and load json content from request body.
        
        :return: dict
        """
        if self._cached_json_data:
            return self._cached_json_data

        if not self.request.body:
            return None
        try:
            self._cached_json_data = json.loads(self.request.body.decode())
        except json.JSONDecodeError:
            self._cached_json_data = None
        return self._cached_json_data

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages.

        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.

        If this error was caused by an uncaught exception (including
        HTTPError), an ``exc_info`` triple will be available as
        ``kwargs["exc_info"]``.  Note that this exception may not be
        the "current" exception for purposes of methods like
        ``sys.exc_info()`` or ``traceback.format_exc``.
        """
        self.clear()    # clean all chunks
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            cls, exc, trace_back = kwargs['exc_info']
            if isinstance(exc, exceptions.APIHTTPError):
                self.set_header('Content-Type', 'application/json')
                self.write(exc.reason)
            else:
                self.set_header('Content-Type', 'text/plain')
                for line in traceback.format_exception(*kwargs["exc_info"]):
                    self.write(line)
            self.finish()
        else:
            error_message = self._reason
            if 'message' in kwargs:
                error_message = kwargs.get('message')
            self.finish({
                'status': status_code,
                'errors': error_message
            })


class AuthTokenRequiredMixin(RequestHandler):
    """
    Authentication mixin.
    Would be used for token communication with server.
    """

    REQUIRED = True

    @tornado.gen.coroutine
    def prepare(self):
        """
        Check request headers for authentication data.
        """
        token = self.request.headers.get(
            self.settings['auth_header_name'],
            self.get_argument('auth_token', None)
        )
        if token is None and self.REQUIRED:
            raise exceptions.APIHTTPError(
                HTTPStatus.UNAUTHORIZED,
                reason={'detail': "Incorrect auth token"}
            )
        self.request.auth_token = yield self.settings['db'].tokens.find_one({'key': token})
        if self.request.auth_token is None and self.REQUIRED:
            raise exceptions.APIHTTPError(
                HTTPStatus.UNAUTHORIZED,
                reason={'detail': "Incorrect auth token"}
            )


class LimitOffsetMixin(RequestHandler):

    LIMIT_KEY = 'limit'
    OFFSET_KEY = 'offset'

    def get_page_data(self) -> (int, int):
        """
        Return limit/offset data from GET params.
        :return: tuple (limit, offset)
        """
        form = LimitOffsetForm(data={
            'limit': self.get_argument(self.LIMIT_KEY, 0),
            'offset': self.get_argument(self.OFFSET_KEY, 0),
        })
        limit, offset = self.settings['page_size'], 0
        if form.validate():
            limit, offset = int(form.data.get('limit')), \
                            int(form.data.get('offset'))
            if limit <= 0:
                limit = self.settings['page_size']
        return limit, offset
