# response contains session cookie that matches configured name.

from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
import cookies
import jwt
import json

from wsgi_jwt_session import JWTSessionMiddleware


def counter_app(environ, start_response):
    session = environ['my_jwt_session']
    session['counter'] = session.get('counter', 0) + 1
    start_response("200 OK", [('Content-Type', 'text/plain')])
    return 'Current counter value: %s' % session['counter']


def test_cookie_name_setting():
    app = JWTSessionMiddleware(
        counter_app,
        secret_key='Use something big and randomly-generated here',
        wsgi_name='my_jwt_session',
        cookie_name='my_jwt_session',
    )
    c = Client(app, BaseResponse)
    resp = c.get('/')
    cookie = cookies.parse_one_response(resp.headers['Set-Cookie'])
    #encoded_body = cookie['value'].split('.')[1]
    #json_body = jwt.utils.base64url_decode(encoded_body)
    #parsed_body = json.loads(json_body)
    assert cookie['name'] == 'my_jwt_session'


def test_wsgi_name_setting():
    def assertion_app(environ, start_response):
        assert isinstance(environ['test_session'], dict)
        start_response("200 OK", [('Content-Type', 'text/plain')])
        return 'OK'
    app = JWTSessionMiddleware(
        assertion_app,
        secret_key='Use something big and randomly-generated here',
        wsgi_name='test_session',
        cookie_name='my_jwt_session',
    )
    c = Client(app, BaseResponse)
    c.get('/')



# wsgi environ contains item that matches configured name.

# cookie set from app can be deserialized.

# cookie that's been tampered with will be dropped.
