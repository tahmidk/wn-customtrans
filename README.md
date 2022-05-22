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
