# wn-customtrans
A web app extension to the wn-downtrans project built on the Flask framework

# Setting up the development server
##First Time Setup
###Setup python3 virtual environment
$ cd .../wn-customtrans
$ python -m venv venv
$ ./venv/Scripts/activate
$ pip install -r requirements.txt

##Recurring Setup
###Run development server
$ ./venv/Scripts/activate
$ set FLASK_ENV=development
$ python run.py

#Accessing Development Server Webapp
In Chrome: http://localhost:5000/

#Handling database migration
Sometimes, an update to this web app is accompanied by a change in the SQLAlchemy database schema. This section describes what to do on the release Web Server (RPi) to smoothly migrate the existing database from old version to the current. The following commands takes place in the root of the project: wn-customtrans/

$ flask db init
$ flask db migrate -m "Migration description"
$ flask db upgrade

#Extra steps needed to run
A Redis server is needed to run a Celery daemon
	Install Redis on Windows 10: https://www.youtube.com/watch?v=_nFwPTHOMIY&ab_channel=Redis

A Celery daemon is required to launch Flask without hang


