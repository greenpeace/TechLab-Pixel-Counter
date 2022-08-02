# Python Flask Framework - created a CRUD API for counts
Create an CRUD API.

# GCP Cloud Run Button

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/greenpeace/TechLab-Pixel-Counter.git)


# How it works

This is an API driven pixel approach based on the CRUD API concept.


## Create

You can use multiple counters in the same database by changing the id to the NRO name, like this
    
    ```
    {
    "id": "NRO-1",
    "count": 0
    }
    ```

http://127.0.0.1:8080/add?id=NRO-1&count=0

and

http://127.0.0.1:8080/add?id=NRO-2&count=0


## Read

Read a specific NRO count
http://127.0.0.1:8080/list?id=GPI

Read all NRO Count
http://127.0.0.1:8080/list?id=GPI


## Signup


## Update
You can update a counter or reset it by
http://127.0.0.1:8080/update?id=GPI&count=<a number>


## Delete
You can delete a counter 

http://127.0.0.1:8080/delete?id=GPI

# Other endpoints


## Show counter using iframe
If your system has problems inserting CSS and Javascript in the pages, you can use an iframe

<iframe src="https://127.0.0.1:8080/counter?id=GPI" width="200" height="40" frameborder=0 style="overflow:hidden;" scrolling="no" /></iframe>


To increase the counter you will put a pixel on the thank you page of the petition. Be careful that it is used only when someone has signed the petition. The pixel is practically invisible. The html code to put it is:

<img src="https://127.0.0.1:8080/count?id=GPI" alt="" />


# Build and launch to Cloud Run

# Deploy
Log in to gcloud as the user that will run Docker commands.

To configure authentication with user credentials, run the following command:

```
gcloud auth login
```

To configure authentication with service account credentials, run the following command:

```
gcloud auth activate-service-account ACCOUNT --key-file=KEY-FILE

gcloud auth activate-service-account newsapi@social-climate-tech.iam.gserviceaccount.com --key-file=/Users/torbjornzetterlund/Documents/service_accounts/social-climate-tech-67aafbddc5ed.json
```

Where

ACCOUNT is the service account name in the format [USERNAME]@[PROJECT-ID].iam.gserviceaccount.com. You can view existing service accounts on the Service Accounts page of console or with the command gcloud iam service-accounts list
KEY-FILE is the service account key file. See the Identity and Access Management (IAM) documentation for information about creating a key.
Configure Docker with the following command:

```
gcloud auth configure-docker
```

```
gcloud auth configure-docker europe-docker.pkg.dev
```

Europe Docker is the Docker registry that is used for the Docker image.
```
$ docker build -t eu.gcr.io/social-climate-tech/pixelcount .
$ docker push eu.gcr.io/social-climate-tech/pixelcount
```

US
```
$ docker build -t gcr.io/social-climate-tech/pixelcount .
$ docker push gcr.io/social-climate-tech/pixelcount
```

## Deploy Yaml database
```
gcloud builds submit --config cloudbuild.yaml .
```

<a href="https://cloud.google.com/compute/docs/regions-zones/#available">Regions and zones</a>

<a href="https://cloud.google.com/container-registry/docs/pushing-and-pulling">Pushing and pulling images</a>


# Push To Multiple Repositories

I use two git Repositories
GitLab for internal Use and deployment
GitHub for public use

From the root folder of your project, add both repositories to the remotes:

```
git remote add origin https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
git remote add copy https://github.com/greenpeace/TechLab-Pixel-Counter.git
```

Run the git remote -v command to ensure that both remotes were successfully added

Now you are able to perform a push to the selected remote by specifying it in the git push command:

```
git push origin master
git push copy master
```

Create a new remote named "all", and add GitLab and GitHub URLs to it

```
git remote add all https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
git remote set-url all --add --push https://gitlab.greenpeace.org/gp/git/global-apps/techlab-coding-team/techlab-tracking-pixel.git
git remote set-url all --add --push https://github.com/greenpeace/TechLab-Pixel-Counter.git
```

```
git push all main
```
