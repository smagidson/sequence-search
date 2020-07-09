# Requirements: docker, python, pip, npm
# Result will be the app GUI running at localhost:3000
# Backend will run at localhost:8000
# A Postgres DB hosted in Docker will run at localhost:5432

# run DB, add needed database
docker pull postgres
docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres
sleep 2
docker exec `docker ps | gawk '{ if ($2 == "postgres") print $1 }'` createdb -U postgres searchsequences

# install dependencies and get server running at localhost:8000
cd server
pip install pipenv
pipenv install
pipenv run python ./manage.py migrate
pipenv run python ./manage.py runserver &

# run front-end at localhost:3000
cd ../webpage
mv src/constants.js src/constants_remote.js
mv src/constants_local.js src/constants.js
npm install
npm start