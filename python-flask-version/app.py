# Python standard libraries
import json
import os
import logging
import sqlite3
import base64
import werkzeug
import time

# Third-party libraries
from flask import Flask, request, url_for, redirect, jsonify, render_template, abort
from google.cloud.firestore import Increment
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User
from getsecret import getsecrets

# Install Google Libraries
import google.cloud.logging
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

## Logging Client
client = google.cloud.logging.Client()

# configure local or cloud
try:
    from config import BUCKET # only cloud
    # Get the sites environment credentials
    project_id = os.environ["PROJECT"]
except:
    project_id = 'social-climate-tech'

## Get start time
start_time = time.time()

# Get the secret for Service Account
client_secret = getsecrets("service-account-key",project_id)

# initialize firebase sdk
CREDENTIALS = credentials.ApplicationDefault()
firebase_admin.initialize_app(CREDENTIALS, {
    'projectId': project_id,
})

# Configuration
#GOOGLE_CLIENT_ID = CREDENTIALS
#GOOGLE_CLIENT_SECRET = CREDENTIALS.client_secret
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def page_not_found(e):
  return render_template('404.html'), 404

def internal_server_error(e):
  return render_template('500.html'), 500

# Initialize Flask App
app = Flask(__name__)
#app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
#try:
#    init_db_command()
#except sqlite3.OperationalError:
    # Assume it's already been created
 #   pass

# OAuth 2 client setup
#client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Initialize Firestore DB
db = firestore.client()
# Counters firestore collection
counter_ref = db.collection(u'counters')
# Donation firestore collection
donation_ref = db.collection(u'donation')

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

logging.info("Start processing Function")

# Register Error Handlers
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)
#
# API Route Default displays a webpage
#
@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('index.html', **locals())
    else:
        return render_template('login.html', **locals())

@app.route('/')
def main():
    return render_template('index.html', **locals())

#
# Login
# 
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

#
# Logout
#
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#
# Login Callback
# 
@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    
    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route('/add', methods=['POST'])
def create():
    try:
        id = request.json['id']
        counter_ref.document(id).set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

#
# API Route add with GET a counter by ID - requires json file body with id and count
#   /addset?id=<id>&count=<count>
#
@app.route('/addset', methods=['GET'])
def createset():
    try:
        counter_id = request.args.get('id')
        counter_ref.document(counter_id).set(request.args)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route('/list', methods=['GET'])
def read():
    try:
        # Check if ID was passed to URL query
        counter_id = request.args.get('id')    
        if counter_id:
            counter = counter_ref.document(counter_id).get()
            return jsonify(u'{}'.format(counter.to_dict()['count'])), 200
        else:
            all_counters = [doc.to_dict() for doc in counter_ref.stream()]
            return render_template('list.html', output=all_counters)
#            return jsonify(all_counters), 200
    except Exception as e:
        return f"An Error Occured: {e}"
#
# API Route Update a counter by ID - requires json file body with id and count
# API endpoint /update?id=<id>&count=<count>
#
@app.route('/update', methods=['POST', 'PUT'])
def update():
    try:
        id = request.json['id']
        counter_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

#
# API Route Increase Counter by ID - requires json file body with id and count
# API endpoint /counter 
# json {"id":"GP Canada","count", 0}
#
@app.route('/counter', methods=['POST', 'PUT'])
def counter():
    try:
        id = request.json['id']
        counter_ref.document(id).update({u'count': Increment(1)})
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

##
# The count route used for pixel image to increase a count using a GET request
# API endpoint /count?id=<id>
##
@app.route('/count', methods=['GET'])
def count():
    try:
        id = request.args.get('id')  
        counter_ref.document(id).update({u'count': Increment(1)})
        return base64.b64decode(b'='), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
##
# The API endpoint allows the user to get the endpoint total defined  by id
# API endpoint /signup?id=<id>
##
@app.route('/signups', methods=['POST', 'PUT'])
def signups():    
    try:
        if request.method == "POST":
            id = request.form['id']
            counter = counter_ref.document(id).get()
            output = f"{ counter.to_dict()['count'] }"            
            return render_template('index.html', output=output)
        return render_template('index.html', output="Not NGO name has been given")
    except Exception as e:
        return render_template('index.html', output="An Error Occured: {e}")
        #return f"An Error Occured: {e}" 


##
# The API endpoint is an example on how you can submit a form acapture the data and submit it to the database
# API endpoint /donation
# Post request with json form data{"id":"GP Canada","count", 0}
##
@app.route('/donationform', methods=['GET'])
def donationform():
    return render_template('donation.html',**locals())

##
# The API endpoint is an example on how you can submit a form acapture the data and submit it to the database
# API endpoint /donation
# Post request with json form data{"id":"GP Canada","count", 0}
##
@app.route('/donation', methods=['POST', 'PUT'])
def donation():    
    try:
        donation_ref.document().set(request.form)
        return render_template('donation.html',**locals())
        #return jsonify({"success": True}), 200
    except Exception as e:
        return render_template('donation.html', output="An Error Occured: {e}")
        #return f"An Error Occured: {e}" 
        
#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route('/donationlist', methods=['GET'])
def donationlist():
    try:
        donation = [doc.to_dict() for doc in donation_ref.stream()]
        return render_template('donationlist.html', output=donation), 200
    except Exception as e:
        return f"An Error Occured: {e}"

#
# API Route Delete a counter by ID /delete?id=<id>
# API Enfpoint /delete?id=<id>
#
@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    try:
        # Check for ID in URL query
        counter_id = request.args.get('id')
        counter_ref.document(counter_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
#
# 404 Page not found    
#
@app.errorhandler(404)
def not_found_error(error):
    logging.info(f'404 Page Not Found')
    return render_template('404.html'), 404

#
# 500 error trying to access the API endpoint
#
@app.errorhandler(werkzeug.exceptions.HTTPException)
def internal_error(error):
    logging.info(f'500 System Error')
    return render_template('500.html'), 500

# 
# Get Google Credentials
#
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

#
# Setting up to serve on port 8080
#
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)
