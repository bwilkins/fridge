#!/usr/bin/env python
# -*- coding: utf8 -*-
import os, sys
DIRNAME = os.path.dirname(__file__)
if not DIRNAME:
    DIRNAME = os.getcwd()
sys.path.append(DIRNAME)

import bottle
from bottle import route, run, get, post, request, response, redirect, static_file
from bottle import jinja2_view as view

bottle.TEMPLATE_PATH.append(DIRNAME + '/templates/')

from beaker.middleware import SessionMiddleware

import bcrypt

from ConfigParser import ConfigParser
import time
from hashlib import sha1
from base64 import b64encode, b64decode
from datetime import datetime

import database

config = ConfigParser()
config.read('config.cfg')

_, Session = database.init(config.get('database', 'url'), debug=True)
session = Session()

session_opts = {
    'session.type': 'file',
    'session.data_dir': './data',
    'session.lock_dir': './lock',
    'session.auto': True
}

sessiontype = config.get('session', 'type')
session_opts['session.type'] = sessiontype
if sessiontype in ('ext:memcached', 'ext:database'):
    session_opts['session.url'] = config.get('session', 'url')

app = SessionMiddleware(bottle.app(), session_opts)

#Helper functions
def is_admin():
    s = request.environ.get('beaker.session')
    return s.get('is_admin', False)

def is_logged_in():
    s = request.environ.get('beaker.session')
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

def not_logged_in(f):
    def wrapper(*args, **kwargs):
        if is_logged_in():
            redirect('/')
        return f(*args, **kwargs)
    return wrapper

def generate_csrf():
    csrf = b64encode(sha1(str(time.time())).digest())
    s = request.environ.get('beaker.session')
    s['csrf'] = csrf
    s.save()

    return csrf

def check_csrf():
    s = request.environ.get('beaker.session')
    return s['csrf'] == request.POST['csrf']

def do_login(user):
    s = request.environ.get('beaker.session')
    s['is_logged_in'] = datetime.now()
    s['logged_in_id'] = user.id
    s['is_admin'] = user.isadmin
    s.save()


#Route handlers
@route('/static/:filename')
def send_static(filename):
    return static_file(filename, root=DIRNAME+'/static/')

@route('/')
@view('home.html')
def home():
    return {}

@get('/login')
@view('login.html')
@not_logged_in
def login():
    return {'csrf_nonce': generate_csrf()}

@post('/login')
@not_logged_in
def process_login():
    s = request.environ.get('beaker.session')
    user = session.query(database.User).filter_by(email=request.POST['email']).first()
    try:
        password_check = user is not None and bcrypt.hashpw(request.POST['password'], user.password) == user.password
        if check_csrf() and password_check:
            do_login(user)
            redirect('/')
        redirect('/login')
    except (KeyError, AttributeError) as e:
        return "You fucked up! " + e.message

@route('/logout')
def logout():
    s = request.environ.get('beaker.session')
    if 'is_logged_in' in s:
        del s['is_logged_in']
        del s['logged_in_id']
        s.save()

    redirect('/')

@get('/register')
@view('register.html')
def register_view():
    if is_logged_in():
        redirect('/already_registered')

    return {'csrf_nonce': generate_csrf()}

@route('/already_registered')
def already_registered():
    return "Already Registered!"

@post('/register')
def register():
    post = request.POST
    user = session.query(database.User).filter_by(email=post['email']).first()
    if user is not None:
        redirect('/already_registered')

    if post['password'] != post['confirmpassword'] or not check_csrf():
        redirect('/you_fucked_up')

    password = bcrypt.hashpw(post['password'], bcrypt.gensalt(14))

    user = database.User(post['email'], password)
    session.add(user)
    session.commit()

    user = session.query(database.User).filter_by(email=post['email']).first()


    do_login(user)

    redirect('/')


@route('/user')
@route('/user/:email')
@require_login()
def userdetails(email=None):
    return email

@route('/users')
@require_login(require_admin=True)
def userlist():
    return ''

@get('/item/:code/edit')
@view('edititem.html')
@require_login(require_admin=True)
def edititem_view(code):
    item = session.query(database.Item).filter_by(code=code).first()
    if not item:
        redirect('/')
    categories = session.query(database.ItemCategory).all()
    return {"item": item, "categories": categories, "is_admin": is_admin()}

@post('/item/:code/edit')
@require_login(require_admin=True)
def edititem(code):
    post = request.POST
    item = session.query(database.Item).filter_by(id=post['id']).first()
    if not item:
        redirect('/')
    for key in post:
        print key, post[key]
        if hasattr(item, key) and getattr(item,key) != post[key]:
            setattr(item, key, post[key])

    session.add(item)
    session.commit()

    redirect('/item/%s' % item.code)

@get('/item/add')
@view('additem.html')
@require_login()
def additem_view():
    categories = session.query(database.ItemCategory).all()
    return {"is_admin": is_admin(), "categories": categories}

@post('/item/add')
@require_login()
def additem():
    post = request.POST
    wishlist = not is_admin() or post.get('wishlist', False)
    cost = post['cost'] if is_admin() else 0;
    item = database.Item(post['code'], post['name'], cost, post['category'], description=post['description'], wishlist=wishlist)
    session.add(item)
    session.commit()
    redirect('/item/%s' % post['code'])

@route('/item/:code')
@view('itemdetails.html')
def itemdetails(code):
    item = session.query(database.Item).filter_by(code=code).first()
    return {"item": item}

@route('/items/wishlist')
def item_wishlist():
    return ''

@get('/items/category/add')
@view('additemcategory.html')
@require_login(require_admin=True)
def additemcategory_view():
    return {}

@post('/items/category/add')
@view('additemcategory.html')
@require_login(require_admin=True)
def additemcategory():
    post = request.POST
    category = database.ItemCategory(post['name'])
    session.add(category)
    session.commit()
    return redirect('/')

@route('/items')
@route('/items/category/:categoryname')
def item_list(categoryname=None):
    return ''


if __name__ == '__main__':
    run(app=app, host='0.0.0.0', port=8080)
