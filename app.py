# Python standard libraries
import os
import logging
import base64
import werkzeug

# Third-party libraries
from flask import Flask, session, request, url_for, redirect, jsonify, render_template, abort, flash
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
from firebase_admin import credentials, firestore
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
    os.environ['GCP_PROJECT'] = 'make-smthng-website'    
    # Get project id to intiate
    project_id = os.environ["GCP_PROJECT"]

# Get the secret for Service Account
client_secret_details = getsecrets("client-secret-key",project_id)
app_secret_key = getsecrets("app_secret_key",project_id)
restrciteddomain = getsecrets("restrciteddomain",project_id)

# initialize firebase sdk
CREDENTIALS = credentials.ApplicationDefault()
firebase_admin.initialize_app(CREDENTIALS, {
    'projectId': project_id,
})

# Create the Flask application error handlers
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
GOOGLE_CLIENT_ID = client_secret_details
#set the path to where the .json file you got Google console is
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
#Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
flow = Flow.from_client_secrets_file( 
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
            ],
    #and the redirect URI is the point where the user will end up after the authorization
    #redirect_uri="http://127.0.0.1:8080/callback"
    redirect_uri="https://pixelcounter.greenpeace.org/callback"   
)

# Initialize Firestore DB
db = firestore.client()
# Counters firestore collection
counter_ref = db.collection(u'counters')
# Allowed origion collection
allowedorigion_ref = db.collection(u'allowedorigion')
# Allowed origion collection
emailhash_ref = db.collection(u'amialhash')

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
    # Renaming the function name:
    #wrapper.__name__ = function.__name__
    return wrapper

#
# API Route Default displays a webpage
#
@app.route("/")
def index():
    return render_template('login.html', **locals())

@app.route("/main", endpoint='main')
@login_is_required
def main():
    return render_template('index.html', **locals())

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

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
    
    #
    # This code is to limit the login to a specific domain
    #
    email = id_info.get("email")
    if email.split('@')[1] != restrciteddomain:
        flash('Login Failed - You do not have a @greenpeace.org email')
        return redirect(url_for('index'))
        
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
@app.route("/add", methods=['POST'], endpoint='create')
@login_is_required
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
@app.route("/addset", methods=['GET'], endpoint='createset')
@login_is_required
def createset():
    try:
        counter_id = request.args.get('id')
        counter_ref.document(counter_id).set(request.args)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/addlist", methods=['GET'], endpoint='addlist')
@login_is_required
def addlist():
    return render_template('listadd.html', **locals())
 
#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/documentation", methods=['GET'], endpoint='documentation')
@login_is_required
def documentation():
    return render_template('documentation.html', **locals())
       
#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/createlist", methods=['POST'], endpoint='createlist')
@login_is_required
def createlist():
    try:
        id = request.form.get('id')
        
        data = {
            u'id': request.form.get('id'),
            u'nro': request.form.get('nro'),
            u'url': request.form.get('url'),
            u'count': int(request.form.get('count')),
            u'contactpoint': request.form.get('contactpoint'),
            u'campaign': request.form.get('campaign'),
        }
        
        counter_ref.document(id).set(data)
        flash('Data Succesfully Submitted')
        return redirect(url_for('read'))
    except Exception as e:
        flash('An Error Occvured')
        return f"An Error Occured: {e}"
#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route("/list", methods=['GET'], endpoint='read')
@login_is_required
def read():
    try:
        # Check if ID was passed to URL query
        id = request.args.get('id')    
        if id:
            counter = counter_ref.document(id).get()
            return jsonify(u'{}'.format(counter.to_dict()['count'])), 200
        else:
            all_counters = [doc.to_dict() for doc in counter_ref.stream()]
            return render_template('list.html', output=all_counters)
    except Exception as e:
        return f"An Error Occured: {e}"

#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route("/listedit", methods=['GET'], endpoint='listedit')
@login_is_required
def listedit():
    try:
        # Check if ID was passed to URL query
        counter_id = request.args.get('id')
        counter = counter_ref.document(counter_id).get()
        return render_template('listedit.html', ngo=counter.to_dict())
#            return jsonify(u'{}'.format(counter.to_dict()['count'])), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
#
# API Route Delete a counter by ID /delete?id=<id>
# API Enfpoint /delete?id=<id>
#
@app.route("/listdelete", methods=['GET', 'DELETE'])
def listdelete():
    try:
        # Check for ID in URL query
        id = request.args.get('id')
        counter_ref.document(id).delete()
        return redirect(url_for('read'))
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
# API Route Update a counter by ID - requires json file body with id and count
# API endpoint /update?id=<id>&count=<count>
#
@app.route("/updateform", methods=['POST', 'PUT'], endpoint='updateform')
@login_is_required
def updateform():
    try:
        id = request.form['id']
        
        data = {
            u'id': request.form.get('id'),
            u'nro': request.form.get('nro'),
            u'url': request.form.get('url'),
            u'count': int(request.form.get('count')),
            u'contactpoint': request.form.get('contactpoint'),
            u'campaign': request.form.get('campaign'),
        }
        counter_ref.document(id).update(data)
        return redirect(url_for('read'))
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
        # Check if Remote Host is in the allowed list        
        allowed_origin_list = []
        for doc in allowedorigion_ref.stream():
            allowed_origin_list.append(doc.to_dict()['domain'])
        if 'REMOTE_HOST' in request.environ and request.environ['REMOTE_HOST'] in allowed_origin_list:
            # On allowed lsut, check if ID was passed to URL query
            email_hash = request.args.get('email_hash')
            if email_hash is not None:
                docRef = emailhash_ref.where('email_hash', '==', email_hash).get()
                documents = [d for d in docRef]
                # Check if hash value already exixsts in the database
                if len(documents):
                    # If exists, don not increase count by 1
                    return base64.b64decode(b'='), 200
                else:
                    # Add hashed email to database
                    data = {
                        u'email_hash': email_hash,
                    }
                    emailhash_ref.document().set(data)
            # Add Counter
            id = request.args.get('id')  
            counter_ref.document(id).update({u'count': Increment(1)})
            counter_ref.document('totals').update({u'count': Increment(1)})
            return base64.b64decode(b'='), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
##
# The API endpoint allows the user to get the endpoint total defined  by id
# API endpoint /signup?id=<id>
##
@app.route("/signup", methods=['POST', 'PUT'], endpoint='signup')
@login_is_required
def signup():    
    try:
        if request.method == "POST":
            id = request.form['id']
            counter = counter_ref.document(id).get()
            output = f"{ counter.to_dict()['count'] }"            
            return render_template('index.html', output=output)
        return render_template('index.html', output="Not NGO name has been given")
    except Exception as e:
        return render_template('index.html', output="An Error Occured: {e}")
        
##
# The API endpoint allows the user to get the endpoint total defined  by id
# API endpoint /signup?id=<id>
##
@app.route("/signups", methods=['GET'], endpoint='signups')
def signup():    
    try:
        id = request.args.get('id')
        counter = counter_ref.document(id).get()
        output = counter.to_dict()['count']            
        return jsonify({"unique_count": output, "id": id}), 200
    except Exception as e:
        return f"An Error Occured: {e}" 

#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/allowedlistadd", methods=['GET'], endpoint='allowedlistadd')
@login_is_required
def allowedlistadd():
    return render_template('allowedlistadd.html', **locals())
 
#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route("/allowedlist", methods=['GET'], endpoint='allowedlist')
@login_is_required
def allowedlist():
    try:
        allowedlist = []     
        for doc in allowedorigion_ref.stream():
            don = doc.to_dict()
            don["docid"] = doc.id
            allowedlist.append(don)

        return render_template('allowedlist.html', allowed=allowedlist)
    except Exception as e:
        return f"An Error Occured: {e}"
    
#
# API Route add a counter by ID - requires json file body with id and count
#
@app.route("/allowedlistcreate", methods=['POST'], endpoint='allowedlistcreate')
@login_is_required
def allowedlistcreate():
    try:
        id = request.form.get('id')        
        data = {
            u'id': request.form.get('id'),
            u'domain': request.form.get('domain')
        }
        
        allowedorigion_ref.document(id).set(data)
        flash('Data Succesfully Submitted')
        return redirect(url_for('allowedlist'))
    except Exception as e:
        flash('An Error Occvured')
        return f"An Error Occured: {e}"

#
# API Route Update a counter by ID - requires json file body with id and count
# API endpoint /update?id=<id>&count=<count>
#
@app.route("/allowedlistupdate", methods=['POST', 'PUT'], endpoint='allowedlistupdate')
@login_is_required
def allowedlistupdate():
    try:
        id = request.form['id']
        data = {
            u'id': request.form.get('id'),
            u'domain': request.form.get('domain')
        }
        allowedorigion_ref.document(id).update(data)
        return redirect(url_for('allowedlist'))
    except Exception as e:
        return f"An Error Occured: {e}"    
    
#
# API Route list all or a speific counter by ID - requires json file body with id and count
#
@app.route("/allowedlistedit", methods=['GET'], endpoint='allowedlistedit')
@login_is_required
def allowedlistedit():
    try:
        allowedlists = []
        # Check if ID was passed to URL query
        id = request.args.get('id')
        allowedlist = allowedorigion_ref.document(id).get()
        don = allowedlist.to_dict()
        don["docid"] = allowedlist.id
        allowedlists.append(don)
        
        return render_template('allowedlistedit.html', ngo=don)
    except Exception as e:
        return f"An Error Occured: {e}"
        
#
# API Route Delete a counter by ID /delete?id=<id>
# API Enfpoint /delete?id=<id>
#
@app.route("/allowedlistdelete", methods=['GET', 'DELETE'], endpoint='allowedlistdelete')
def allowedlistdelete():
    try:
        # Check for ID in URL query
        id = request.args.get('id')
        allowedorigion_ref.document(id).delete()
        return redirect(url_for('allowedlist'))
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
        id = request.args.get('id')
        counter_ref.document(id).delete()
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
