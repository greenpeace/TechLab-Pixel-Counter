# Required Imports
# app.py
import os
import base64
import werkzeug
from flask import Flask, request, jsonify, render_template, abort
from google.cloud.firestore import Increment
from firebase_admin import credentials, firestore, initialize_app

#client = secretmanager.SecretManagerServiceClient()
# Get the sites environment credentials
#project_id = os.environ["PROJECT_NAME"]
project_id = 'social-climate-tech'

def page_not_found(e):
  return render_template('404.html'), 404

def internal_server_error(e):
  return render_template('500.html'), 500

# Initialize Flask App
app = Flask(__name__)

# initialize firebase sdk
cred = credentials.Certificate('./key.json')
initialize_app(cred)

# Initialize Firestore DB
#cred = credentials.ApplicationDefault()
#firebase_admin.initialize_app(cred, {
#    'projectId': project_id,
#})
# Intialize Firebase Client for DB
db = firestore.client()
# Counters firestore collection
counter_ref = db.collection(u'counters')
# Donation firestore collection
donation_ref = db.collection(u'donation')

# Register Error Handlers
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)
#
# API Route Default displays a webpage
#
@app.route('/')
def main():
    return render_template('index.html', **locals())

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
    return render_template('404.html'), 404

#
# 500 error trying to access the API endpoint
#
@app.errorhandler(werkzeug.exceptions.HTTPException)
def internal_error(error):
    return render_template('500.html'), 500

#
# Setting up to serve on port 8080
#
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)
