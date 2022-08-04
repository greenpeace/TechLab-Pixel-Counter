# Python standard libraries
import os
import logging
import base64
import werkzeug
import time

# Third-party libraries
from flask import Flask, session, request, url_for, redirect, jsonify, render_template, abort
import pathlib
import requests
from pip._vendor import cachecontrol

# Internal imports
from getsecret import getsecrets

# Install Google Libraries
from google.cloud.firestore import Increment
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import google.cloud.logging
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

## Logging Client
client = google.cloud.logging.Client()

# configure local or cloud
try:
    from config import BUCKET # only cloud
    # Get the sites environment credentials
    project_id = os.environ["GCP_PROJECT"]
except:
    # Set Local Environment Variables (Local)
    os.environ['GCP_PROJECT'] = 'social-climate-tech'
    os.environ['GOOGLE_CLIENT_ID'] = ''
    os.environ['GOOGLE_CLIENT_SECRET'] = ''
    
    # Get project id to intiate
    project_id = os.environ["GCP_PROJECT"]

## Get start time
start_time = time.time()

# Get the secret for Service Account
client_secret = getsecrets("client-secret-key",project_id)
app_secret_key = getsecrets("app_secret_key",project_id)

# initialize firebase sdk
CREDENTIALS = credentials.ApplicationDefault()
firebase_admin.initialize_app(CREDENTIALS, {
    'projectId': project_id,
})


def page_not_found(e):
  return render_template('404.html'), 404

def internal_server_error(e):
  return render_template('500.html'), 500

# Initialize Flask App
app = Flask(__name__)
#it is necessary to set a password when dealing with OAuth 2.0
app.secret_key = app_secret_key 
#this is to set our environment to https because OAuth 2.0 only supports https environments
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#enter your client id you got from Google console
GOOGLE_CLIENT_ID = client_secret
#set the path to where the .json file you got Google console is
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
#Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
flow = Flow.from_client_secrets_file( 
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],  #here we are specifing what do we get after the authorization
    #and the redirect URI is the point where the user will end up after the authorization
    redirect_uri="http://127.0.0.1:8080/callback"  
)

# Initialize Firestore DB
db = firestore.client()
# Counters firestore collection
counter_ref = db.collection(u'counters')
# Donation firestore collection
donation_ref = db.collection(u'donation')

logging.info("Start processing Function")

# Register Error Handlers
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

#a function to check if the user is authorized or not
def login_is_required(function):
    def wrapper(*args, **kwargs):
        #authorization required
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

#
# API Route Default displays a webpage
#
@app.route("/")
def index():
    return render_template('login.html', **locals())

@app.route("/main")
#@login_is_required
def main():
    return render_template('index.html', **locals())

#
# API Route Default displays a webpage
#
@app.route("/login")  #the page where the user can login
def login():
    #asking the flow class for the authorization (login) url
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

#this is the page that will handle the callback process meaning process after the authorization
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  #state does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    
    #the final page where the authorized users will end up
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    # defing the results to show on the page
    session["google_id"] = id_info.get("sub")  
    session["name"] = id_info.get("name")
    return redirect("/main")
#
# the logout page and function
#
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/add", methods=['POST'])
#@login_is_required
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
@app.route("/addset", methods=['GET'])
#@login_is_required
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
@app.route("/list", methods=['GET'])
#@login_is_required
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
@app.route("/update", methods=['POST', 'PUT'])
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
@app.route("/counter", methods=['POST', 'PUT'])
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
@app.route("/count", methods=['GET'])
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
@app.route("/signups", methods=['POST', 'PUT'])
@login_is_required
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
@app.route("/donationform", methods=['GET'])
#@login_is_required
def donationform():
    return render_template('donation.html',**locals())

##
# The API endpoint is an example on how you can submit a form acapture the data and submit it to the database
# API endpoint /donation
# Post request with json form data{"id":"GP Canada","count", 0}
##
@app.route("/donation", methods=['POST', 'PUT'])
#@login_is_required
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
@app.route("/donationlist", methods=['GET'])
#@login_is_required
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
@app.route("/delete", methods=['GET', 'DELETE'])
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
# Setting up to serve on port 8080
#
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)
