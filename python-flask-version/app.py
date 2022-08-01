# Required Imports
# app.py
import os
from flask import Flask, request, jsonify, render_template
from google.cloud.firestore import Increment
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

#client = secretmanager.SecretManagerServiceClient()
# Get the sites environment credentials
#project_id = os.environ["PROJECT_NAME"]
project_id = 'social-climate-tech'

def page_not_found(e):
  return render_template('404.html'), 404

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
counter_ref = db.collection(u'counters')

app.register_error_handler(404, page_not_found)

@app.route('/')
def main():
    return render_template('index.html', **locals())

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
            return render_template('index.html', output=jsonify(all_counters))
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

##
# The count route used for pixel image to make a count using a GET request
##
@app.route('/count', methods=['GET'])
def count():
    try:
        id = request.args.get('id')  
        counter_ref.document(id).update({u'count': Increment(1)})
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
##
# The an NROs signups from the pixel image
##
@app.route('/signups', methods=['POST', 'PUT'])
def signups():    
    try:
        if request.method == "POST":
            counter_id = request.form['id']
            counter = counter_ref.document(counter_id).get()
            output = f"{ counter.to_dict()['count'] }"
            return render_template('index.html', output=output)
        return render_template('index.html', output="Not NGO name has been given")
    except Exception as e:
        return render_template('index.html', output="An Error Occured: {e}")
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

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)
#    app.run(threaded=True, host='0.0.0.0', port=port)
