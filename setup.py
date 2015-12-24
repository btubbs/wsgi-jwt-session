from setuptools import setup

setup(
    name='wsgi_jwt_session',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    version='0.0.1',
    url='http://github.com/btubbs/wsgi_jwt_session',
    py_modules=['wsgi_jwt_session'],
    description='A Python WSGI middleware that provides  '
                'sessions via a JWT-encoded cookie.',
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
