from setuptools import setup

setup(
    name='wsgi-jwt-session',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    version='0.0.1',
    url='http://github.com/btubbs/wsgi-jwt-session',
    py_modules=['wsgi_jwt_session'],
    install_requires=[
        'PyJWT>=1.4.0,<2',
        'Werkzeug>=0.10.1',
    ],
    description='A Python WSGI middleware that provides  '
                'sessions via a JSON Web Token-encoded cookie.',
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
