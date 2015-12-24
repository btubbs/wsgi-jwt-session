# wsgi-jwt-session
A Python WSGI middleware that provides sessions via a JWT-encoded cookie.

## Usage

As with any WSGI middleware, wsgi_jwt_session works by wrapping a WSGI
application.  Here is a super simple pure WSGI example.

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

If you access that endpoint repeatedly, using a client with cookie support, you
should see the counter increment each time.  Here's an example using
[HTTPie](https://github.com/jkbrzt/httpie):

    $ http :8000 --session=foo
    HTTP/1.0 200 OK
    Content-Type: text/plain
    Date: Thu, 24 Dec 2015 00:42:41 GMT
    Server: WSGIServer/0.1 Python/2.7.6
    Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb3VudGVyIjoxfQ.L4FO0H7KJXfOfEgLV_N93ByCMk5FU8ZuX2YG4Q9lw8Q; Expires=Fri, 25-Dec-2015 00:42:41 GMT; Max-Age=86400; Path=/

    Current counter value: 1

    $ http :8000 --session=foo
    HTTP/1.0 200 OK
    Content-Type: text/plain
    Date: Thu, 24 Dec 2015 00:42:42 GMT
    Server: WSGIServer/0.1 Python/2.7.6
    Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb3VudGVyIjoyfQ.1FapXphQivj9kYFArjb6I-Jr-2skXk_G5kCTbqJDOA0; Expires=Fri, 25-Dec-2015 00:42:42 GMT; Max-Age=86400; Path=/

    Current counter value: 2

    $ http :8000 --session=foo
    HTTP/1.0 200 OK
    Content-Type: text/plain
    Date: Thu, 24 Dec 2015 00:42:43 GMT
    Server: WSGIServer/0.1 Python/2.7.6
    Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb3VudGVyIjozfQ.L4FI4sYDd_kUSpOBJyse0iww4cgwMsaiCvcS2BsFDBg; Expires=Fri, 25-Dec-2015 00:42:43 GMT; Max-Age=86400; Path=/

    Current counter value: 3

Check the examples folder in the repository for examples with various
frameworks.  (Or if yours isn't there, please add an example and submit a pull
request.)

## Why

There are already lots of Python web frameworks and libraries that provide
session support.  You may wonder why the world needs another one.
The motivation for creating this library came when I was creating single page
apps in which Python served only static files and API endpoints, while the
entire user interface was built with a front end framework like Angular or
React.  I wanted to be able to securely set session values like user IDs, but
also easily share login state with the UI.  The signed cookie implementations in
[Django](https://docs.djangoproject.com/en/1.9/topics/http/sessions/#using-cookie-based-sessions)
and [Flask/Werkzeug](http://werkzeug.pocoo.org/docs/0.11/contrib/securecookie/)
provide lightweight cookie-based sessions, but cannot be easily parsed from
Javascript.  [JSON Web Tokens](http://jwt.io/), on the other hand, could be
easily deserialized in Javascript, allowing the UI to stay in perfect sync with
the user's session, and display things like a user's name, email address, or
avatar URL without needing extra API calls.

## In-browser usage

Obviously, a user's browser will not have
access to your secret key, so it cannot check the cookie's signature.  So your
client side code should only trust the cookie values if they were returned over
https.  The [jwt-decode](https://github.com/auth0/jwt-decode) Javascript library
is designed for this use case.  It ignores the token's signature, and just gives
you back the payload.  You can use it like this:

    function getCookie(name) {
      var value = "; " + document.cookie;
      var parts = value.split("; " + name + "=");
      if (parts.length == 2) return parts.pop().split(";").shift();
    }

    var encodedSession = getCookie('jwtsession');

    console.log(encoded_session)
    // prints eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb3VudGVyIjo1fQ.8iu8bpGFkVKYWtOPqiZ52mrSUyzwgZ_yG8mQ5S5FYlk

    jwt_decode(encoded_session)

    // prints Object {counter: 5}

You can also copy/paste JWT cookie values into the debugger at
[jwt.io](http://jwt.io/) to manually get a quick look inside them.

## Security

There are a few things to keep in mind about the security of sessions managed
this way:

1. By default, a man in the middle who had access to the HTTP headers in your
   app's requests and responses could read session values as they were
   transmitted over the wire. This is not a bug; it's just the way that
   [HMACs](https://en.wikipedia.org/wiki/Hash-based_message_authentication_code)
   work.
2. As long as your secret key stays secret, an end user or man in the middle
   *cannot* alter the session in any way.  Any attempt to do so will result in
   the token's signature being invalid.  Such sessions are automatically dropped
   by the JWTSessionMiddleware.
3. Your client-side Javascript code can read the values stored in the session,
   but not alter them or add new ones.   
Your JS code can also read the session but not alter it.   (using jwt_decode)

 You can prevent this by switching to an alternate [encryption
   algorithm](https://pyjwt.readthedocs.org/en/latest/algorithms.html), but this
   will prevent

