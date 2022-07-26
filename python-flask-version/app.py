# Required Imports
# app.py

import os
from flask import Flask, request, jsonify, render_template
from google.cloud.firestore import Increment
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# Install Google Libraries
from google.cloud import secretmanager

# Setup the Secret manager Client
client = secretmanager.SecretManagerServiceClient()
# Get the sites environment credentials
#project_id = os.environ["PROJECT_NAME"]
project_id = 'social-climate-tech'

def page_not_found(e):
  return render_template('404.html'), 404

# Get the secret for Slackkey
#secret_name = "newsAPISLackKey"
#resource_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#response = client.access_secret_version(request={"name": resource_name})
#slackurl = response.payload.data.decode('UTF-8')

# Initialize Flask App
app = Flask(__name__)

# initialize firebase sdk
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': project_id,
})

db = firestore.client()
counter_ref = db.collection(u'counters')
#counter_ref = db.collection(u'counters').document(u'pixelcounter')
#doc = counter_ref.get()

app.register_error_handler(404, page_not_found)

counter = 1 #or whatever you want to start with

@app.route('/')
def main():
    global counter
    counter += 1
    return str(counter)

@app.route('/add', methods=['POST'])
def create():
    try:
        id = request.json['id']
        counter_ref.document(id).set(request.json['count'])
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
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
            return jsonify(all_counters), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/update', methods=['POST', 'PUT'])
def update():
    try:
        id = request.json['id']
        counter_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/counter', methods=['POST', 'PUT'])
def counter():
    try:
        id = request.json['id']
        counter_ref.document(id).update({u'count': Increment(1)})
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

    
@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    try:
        # Check for ID in URL query
        counter_id = request.args.get('id')
        counter_ref.document(counter_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

port=9988    
#port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
