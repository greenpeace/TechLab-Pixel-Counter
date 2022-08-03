# TechLab Tracking Pixel

Creating a tracking pixel API in Python with Flask, to add a pixel to the end of the page.

The work has been based on two different developed approaches

<a href="https://github.com/greenpeace/gpes-multi-organizations-counter-api">Php version created by GPES</a> - Pixel code. It basically counts a pixel on the thank you page. 

Pros: Easy to implement across different digital marketing platforms.
Cons: Not too accurate. If somebody signs the petition twice, the email will be counted twice. 


GPUK Code. This is the <a href="https://act.greenpeace.org/page/49013/petition/1">counter</a> collate all unique signatures across different platforms. 
Pros: More accurate
Cons: Not all digital platforms are supported. 

# Approaches
In this repostory we have two approaches, first the one based on the GPES work, and the second one based on a micro service approach using Google Cloud Run to run the Python Flask app.

# Included in the repository
The work done by GPES that we have included in the repository, has got an Docker upgrade that we include the file for

# New work
The new work is based on Python Flask web platform, and we have created an  API Server with Python Flask-RESTful.

The Python flask approach includes Docker files for deployment to Google Cloud Run.

For a user account:

gcloud projects add-iam-policy-binding social-climate-tech \
--member='user:tzetter@socialclimate.tech' \
--role='roles/iam.serviceAccountUser'

For a service account:

gcloud projects add-iam-policy-binding social-climate-tech \
--member='serviceAccount:newsapi@social-climate-tech.iam.gserviceaccount.com' \
--role='roles/iam.serviceAccountUser'

# Authentication
https://cloud.google.com/sdk/gcloud/reference/auth/configure-docker
```
gcloud auth configure-docker gcr.io
```

# Troubleshoot Docker Image
docker run -it --rm --entrypoint sh <name-of-image>

gcr.io/social-climate-tech/pixelcounter