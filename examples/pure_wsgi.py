from __future__ import print_function
from wsgiref import simple_server

from wsgi_jwt_session import JWTSessionMiddleware

def app(environ, start_response):
    session = environ['my_jwt_session']
    session['counter'] = session.get('counter', 0) + 1
    start_response("200 OK", [('Content-Type', 'text/plain')])
    return 'Current counter value: %s' % session['counter']

def main():
    wrapped_app = JWTSessionMiddleware(
        app,
        secret_key='Use something big and randomly-generated here',
        wsgi_name='my_jwt_session',
    )
    server = simple_server.make_server('', 8000, wrapped_app)
    print('Listening on port 8000')
    server.serve_forever()

if __name__ == '__main__':
    main()
