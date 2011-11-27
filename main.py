import bottle
from bottle import route, run
from bottle import jinja2_view as view

from beaker.middleware import SessionMiddleware

from ConfigParser import ConfigParser

import database

config = ConfigParser()
config.read('config.cfg')

_, Session = database.init(config.get('database', 'dbpath'), debug=True)

app = SessionMiddleware(bottle.app(), {
            'session.type': 'file',
            'session.cookie_expires': 300,
            'session.data_dir': './data',
            'session.auto': True
      })

@route('/login')
def login():
    return "<h1>Hello!</h1>"

@route('/user')
@route('/user/:username')
def userdetails(username=None):
    return ''

@route('/users')
def userlist():
    return ''

@route('/item/:itemname')
def itemdetails(itemname):
    return ''

@route('/items/wishlists')
@route('/items/wishlist/:username')
def item_wishlist(username=None):
    return ''


@route('/items')
@route('/items/category/:categoryname')
def item_list(categoryname=None):
    return ''

run(app=app, host='localhost', port=8080)
