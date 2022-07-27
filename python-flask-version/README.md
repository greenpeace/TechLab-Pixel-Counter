# Python Flask Framework - created a CRUD API for counts
Create an CRUD API.
 
# Build and launch to Cloud Run

gcloud builds submit --config cloudbuild.yaml .

# GCP Cloud Run Button

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/greenpeace/TechLab-Pixel-Counter.git)


# How it works

This is an API driven pixel approach based on the CRUD API concept.

## Create

You can create a counter by



## Read

## Update

## Delete

# Other endpoints

# Count


$ docker build -t eu.gcr.io/social-climate-tech/pixelcounter .
$ docker push eu.gcr.io/social-climate-tech/pixelcounter

https://cloud.google.com/compute/docs/regions-zones/#available


# Push To Multiple Repositories

I use two git Repositories
GitLab for internal Use and deployment
GitHub for public use

From the root folder of your project, add both repositories to the remotes:

'''
git remote add origin https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
git remote add copy https://github.com/greenpeace/TechLab-Pixel-Counter.git
'''

Run the git remote -v command to ensure that both remotes were successfully added

Now you are able to perform a push to the selected remote by specifying it in the git push command:

'''
git push origin master
git push copy master
'''

Create a new remote named "all", and add GitLab and GitHub URLs to it

'''
git remote add all https://github.com/greenpeace/TechLab-Pixel-Counter.git
git remote set-url all --add --push https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
git remote set-url all --add --push https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
'''

'''
git push all main
'''
