#!/usr/bin/env python

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, g, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from functools import wraps
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///categoryitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session is None:
            return redirect(url_for('showLogin'), next=request.url)
        return f(*args, **kwargs)
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'),
                    200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                    json.dumps('Current user not connected.'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2' +
           '/revoke?token=%s' % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category Information
@app.route('/catalog/<string:category_name>/JSON')
def categoryItemJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    item_info = session.query(Item).filter_by(name=item_name).one()
    return jsonify(item_info=item_info.serialize)


@app.route('/catalog/JSON')
def restaurantsJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(asc(Item.id))
    if 'username' not in login_session:
        return render_template('publiccategory.html', categories=categories,
                               items=items)
    else:
        creator = getUserInfo(login_session['user_id'])
        return render_template('category.html', categories=categories,
                               items=items, creator=creator)


# Show all items
@app.route('/catalog/<string:category_name>/items/')
def showItems(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    if 'username' not in login_session:
        return render_template('publicitems.html',
                               items=items,
                               categories=categories,
                               category=category)
    else:
        creator = getUserInfo(login_session['user_id'])
        return render_template('items.html',
                               items=items,
                               categories=categories,
                               category=category,
                               creator=creator)


# Show item info
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showInfo(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).all()
    item = session.query(Item).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        return render_template('publicinfo.html', item=item)
    else:
        return render_template('info.html', item=item, creator=creator)


# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        category = session.query(Category).filter_by(
                                        name=request.form['category']).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category.id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created!' % (newItem.name))
        return redirect(url_for('showCategories'))
    else:
        creator = getUserInfo(login_session['user_id'])
        return render_template('new.html', creator=creator)


# Edit an item
@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    editedItem = session.query(Item).filter_by(name=item_name).one()
    if editedItem.user_id != login_session['user_id']:
        return render_template('pop_up.html')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            category = session.query(Category).filter_by(
                        name=request.form['category']).one()
            editedItem.category_id = category.id
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategories'))
    else:
        creator = getUserInfo(editedItem.user_id)
        return render_template('edit.html', item=editedItem, creator=creator)


# Delete an item
@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    if itemToDelete.user_id != login_session['user_id']:
        return render_template('pop_up.html')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        creator = getUserInfo(itemToDelete.user_id)
        return render_template('delete.html',
                               item=itemToDelete,
                               creator=creator)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
