# Sequence Search

Searches a set of organisms (given by [NCBI](https://www.ncbi.nlm.nih.gov/guide/proteins/) names) for a given DNA sequence and returns the first match it finds, with information on what protein the sequence is found in (if available) and what position it starts at.

## Run it
### Run locally
#### Prequisites
* docker
* npm
* python 3.5+
* pip
* bash

Run `./run_local.sh` at the root of the directory. It will run the backend Django server at `http://localhost:8000` and the React frontend at `http://localhost:3000`.

### Run remotely
I got this working in AWS Elastic Beanstalk after a lot of grief. It is _almost_ automated, but I couldn't 100% get it.

Prerequisites:
* The database is already created in RDS.
  * It should be publicly accessible.
  * Fill in your own host in the `GB_APP_DB_HOST` environment variable
  * Create a `searchsequences` database on the host
  * When you create the Beanstalk app, its security group should be given access to the DB. 
* The secret variables are saved as secure strings in the parameter store in SSM.
  * `GB_APP_DB_PASSWORD` is the DB password
  * `GB_APP_KEY` is some string that should be hard to guess, which people use to create a user
  * `GB_DJANGO_SECRET_KEY` is a long string used by Django (I don't think this app actually uses it, but it's good practice)

This app runs on AWS's Python 3.6 Beanstalk platform (not the latest, 3.7, which [wasn't working well with Django](https://github.com/aws/elastic-beanstalk-roadmap/issues/68) as of this writing).

I zipped up the contents of the `server` folder and uploaded it to deploy it.

The first deployment will fail because it won't be able to install psycopg2. SSH onto the EC2 instance and run `sudo yum install postgresql-devel`. (I could not find a better solution [than this](https://stackoverflow.com/questions/33747799/psycopg2-on-elastic-beanstalk-cant-deploy-app/34957820#34957820), alas.) Then redeploy. That should succeed.

You will also need to set the `GB_DJANGO_ALLOWED_HOST` environment variable to your backend's URL in Beanstalk.

You can then either point the React code to it (using the `APP_BASE_URL` in `webpage/constants.js`) and either run locally using `npm start`, or deploy it into the world. (I [hosted statically in S3](https://hackernoon.com/hosting-static-react-websites-on-aws-s3-cloudfront-with-ssl-924e5c134455).) Be sure to tweak the `GB_CORS_VALUE` environment variable to match your host.

## Usage
On the front page, you can choose a user name. The key is the same across users. (With more time, I might have explored Django's prepackaged user management, but this suits the need.) Locally, it's `kk`. Remotely, it uses `GB_APP_KEY`.

Once you submit a user name with the correct key, you will see any previous sequence queries, their status, and results. To search for a new sequence, enter it in the text area at the bottom and click "New Search".

The new search will immediately appear in the table with a "pending" status. If this is your first query against the given backend, it may take 30ish seconds to finish (since the server will be downloading genbank files to search). Otherwise, it shouldn't take more than a few seconds (longer when searching for a longer sequence).

The status does not update automatically when it completes. You have to click the "Reload" button at the bottom to see the results.

You can also delete any of your queries by clicking the "Delete" button.

Click "Change user" at the top to "log out".

## Structure
* Frontend React code is in `webpage`.
* Backend server code is in `server`. It is Django.
* Deployment files are in `.ebextensions` (and `server/aws_startup.py`, which worked better for certain steps)

## Other notes

This is my first time writing React, a Django app (and deploying it to Elastic Beanstalk), and using Biopython. I probably violated quite a few conventions and along the way, but hopefully I'll get better in the future.

I used pipenv for dependency management since it seemed like a better system (more similar to npm) than having to remember to do `pip freeze > requirements.txt` before every deploy. But Elastic Beanstalk seems to need requirements.txt, so that's there, too.