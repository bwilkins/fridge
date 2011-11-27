import bottle
from bottle import route, run, get, post
from bottle import jinja2_view as view

from beaker.middleware import SessionMiddleware

from ConfigParser import ConfigParser

import database

config = ConfigParser()
config.read('config.cfg')

_, Session = database.init(config.get('database', 'url'), debug=True)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.lock_dir': './lock',
    'session.auto': True
}

sessiontype = config.get('session', 'type')
session_opts['session.type'] = sessiontype
if sessiontype in ('ext:memcached', 'ext:database'):
    session_opts['session.url'] = config.get('session', 'url')

app = SessionMiddleware(bottle.app(), session_opts)

def is_admin():
    s = bottle.request.environ.get('beaker.session')
    return s.get('is_admin', False)

def is_logged_in():
    s = bottle.request.environ.get('beaker.session')
    return s.get('is_logged_in', False)

def require_login(require_admin=False):
    def wrapper(f):
        def wrapsomemore(*args, **kwargs):
            if not is_logged_in():
                return "Not logged in!"

            if require_admin:
                if not is_admin():
                    return "Not admin!"

            return f(*args, **kwargs)
        return wrapsomemore
    return wrapper


@get('/login')
def login():
    return "<h1>Hello!</h1>"

@post('/login')
def process_login():
    return ''

@route('/user')
@route('/user/:username')
@require_login()
def userdetails(username=None):
    return ''

@route('/users')
@require_login(require_admin=True)
def userlist():
    return ''

@route('/item/:itemname')
def itemdetails(itemname):
    return ''

@route('/items/wishlist')
def item_wishlist():
    return ''


@route('/items')
@route('/items/category/:categoryname')
def item_list(categoryname=None):
    return ''

run(app=app, host='localhost', port=8080)
