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
# Trim excess whitespace when rendering with jinja2
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Add user directory
app.add_url_rule('/user/default/dicts/<path:filename>', endpoint='dict',
                 view_func=app.send_static_file)
app.add_url_rule('/user/default/<path:filename>', endpoint='user',
                 view_func=app.send_static_file)

# Create database instance connected to webapp
db = SQLAlchemy(app)

# Secure web app forms against CSRF
csrf = CsrfProtect(app)

from app import views