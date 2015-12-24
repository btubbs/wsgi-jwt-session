# -*- coding: utf-8 -*-

from Cookie import SimpleCookie

import jwt
from werkzeug._compat import text_type
from werkzeug.contrib.sessions import ModificationTrackingDict
from werkzeug.http import dump_cookie


class JWTCookie(ModificationTrackingDict):

    """Represents a secure cookie.

    Example usage:

    >>> x = JWTCookie({"foo": 42, "baz": (1, 2, 3)}, "deadbeef")
    >>> x["foo"]
    42
    >>> x["baz"]
    (1, 2, 3)
    >>> x["blafasel"] = 23
    >>> x.should_save
    True

    :param data: the initial data, as a dictionary.
    :param secret_key: the secret key.  If not set `None` or not specified
                       it has to be set before :meth:`serialize` is called.
    :param algorithm: A string indicating the algorithm to be used.  Must be
                      supported by the PyJWT library.
    """

    def __init__(self, data=None, secret_key=None, algorithm='HS256'):
        ModificationTrackingDict.__init__(self, data or ())
        # explicitly convert it into a bytestring because python 2.6
        # no longer performs an implicit string conversion on hmac
        if secret_key is not None:
            secret_key = bytes(secret_key)
        self.secret_key = secret_key
        self.algorithm = algorithm

    def __repr__(self):
        return '<%s %s%s>' % (
            self.__class__.__name__,
            dict.__repr__(self),
            self.should_save and '*' or ''
        )

    @property
    def should_save(self):
        """True if the session should be saved.  By default this is only true
        for :attr:`modified` cookies, not :attr:`new`.
        """
        return self.modified

    def serialize(self, expires=None):
        """Serialize the secure cookie into a string.

        If expires is provided, the session will be automatically invalidated
        after expiration when you unseralize it. This provides better
        protection against session cookie theft.

        :param expires: an optional expiration date for the cookie (a
                        :class:`datetime.datetime` object)
        """
        if self.secret_key is None:
            raise RuntimeError('no secret key defined')
        if expires:
            self['exp'] = expires
        return jwt.encode(self, self.secret_key, self.algorithm)

    @classmethod
    def unserialize(cls, string, secret_key, algorithm='HS256'):

        """Load the secure cookie from a serialized string.

        :param string: the cookie value to unserialize.
        :param secret_key: the secret key used to serialize the cookie.
        :return: a new :class:`JWTCookie`.
        """
        if isinstance(string, text_type):
            string = string.encode('utf-8', 'replace')
        if isinstance(secret_key, text_type):
            secret_key = secret_key.encode('utf-8', 'replace')

        items = jwt.decode(string, secret_key, algorithms=[algorithm])
        return cls(items, secret_key, algorithm)

    @classmethod
    def load_cookie(cls, request, key='session', secret_key=None):
        """Loads a :class:`JWTCookie` from a cookie in request.  If the
        cookie is not set, a new :class:`JWTCookie` instanced is
        returned.

        :param request: a request object that has a `cookies` attribute
                        which is a dict of all cookie values.
        :param key: the name of the cookie.
        :param secret_key: the secret key used to decode the cookie.
                           Always provide the value even though it has
                           no default!
        """
        data = request.cookies.get(key)
        if not data:
            return cls(secret_key=secret_key)
        return cls.unserialize(data, secret_key)

    def save_cookie(self, response, key='session', expires=None,
                    session_expires=None, max_age=None, path='/', domain=None,
                    secure=None, httponly=False, force=False):
        """Saves the JWTCookie in a cookie on response object.  All parameters
        that are not described here are forwarded directly to
        :meth:`~BaseResponse.set_cookie`.

        :param response: a response object that has a
                         :meth:`~BaseResponse.set_cookie` method.
        :param key: the name of the cookie.
        :param session_expires: the expiration date of the secure cookie
                                stored information.  If this is not provided
                                the cookie `expires` date is used instead.
        """
        if force or self.should_save:
            data = self.serialize(session_expires or expires)
            response.set_cookie(key, data, expires=expires, max_age=max_age,
                                path=path, domain=domain, secure=secure,
                                httponly=httponly)


class JWTSessionMiddleware(object):
    def __init__(self, app, secret_key, cookie_name='jwtsession',
                 wsgi_name='jwtsession', max_age=86400, algorithm='HS256'):
        self.app = app
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.wsgi_name = wsgi_name
        self.max_age = max_age
        self.algorithm = algorithm

    def __call__(self, environ, start_response):
        # on the way in: if environ includes our cookie, then deserialize it and
        # stick it back into environ as jwtsession.  If environ doesn't include
        # one then make an empty one and stick that in.
        if 'HTTP_COOKIE' in environ:
            cookie = SimpleCookie(environ['HTTP_COOKIE'])
            if self.cookie_name in cookie:
                try:
                    session = JWTCookie.unserialize(
                        cookie[self.cookie_name].value,
                        self.secret_key,
                        self.algorithm
                    )
                except jwt.DecodeError:
                    session = JWTCookie({}, self.secret_key, self.algorithm)
            else:
                session = JWTCookie({}, self.secret_key, self.algorithm)
        else:
            session = JWTCookie({}, self.secret_key, self.algorithm)
        environ[self.wsgi_name] = session


        # on the way out: serialize jwtsession and stick it into headers as
        # 'session'.
        def session_start_response(status, headers, exc_info=None):
            if session.should_save or session == {}:
                # add our cookie to headers
                c = dump_cookie(self.cookie_name,
                                value=environ[self.wsgi_name].serialize(),
                                max_age=self.max_age)
                headers.append(('Set-Cookie', c))
            return start_response(status, headers, exc_info=exc_info)

        return self.app(environ, session_start_response)
