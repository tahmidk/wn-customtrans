#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

from flask import Flask
from flask_wtf.csrf import CsrfProtect
from flask_sqlalchemy import SQLAlchemy

# Initialize and configure Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e0d41ebf1910b2ba'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wnct_database.db'

# Create database instance connected to webapp
db = SQLAlchemy(app)

# Secure web app forms against CSRF
CsrfProtect(app)

from app import views