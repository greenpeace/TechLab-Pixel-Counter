import config
import datetime
import pytz
import firebase_admin
from firebase_admin import credentials, firestore

# Get the sites environment credentials
#project_id = os.environ["PROJECT_NAME"]
project_id = 'social-climate-tech'

# initialize firebase sdk
CREDENTIALS = credentials.ApplicationDefault()
firebase_admin.initialize_app(CREDENTIALS, {
    'projectId': project_id,
})

# get firestore client
db = firestore.client()

db.collection('counter').document().set(+1)  # Add a new doc in collection links with ID shop

var counterRef = db.collection("counter").doc("gpi");
# Atomically add a new NGO to the "regions" array field.
counterRef.update({
    regions: firebase.firestore.FieldValue.arrayUnion("greater_virginia")
});
# Atomically remove a region from the "regions" array field.
counterRef.update({
    regions: firebase.firestore.FieldValue.arrayRemove("east_coast")
});


def generateBlogTopics(prompt1):
    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Generate blog topics on: {}. \n \n 1.  ".format(prompt1),
      temperature=0.7,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return response['choices'][0]['text']
  
def _now():
    return datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
