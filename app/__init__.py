#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

from flask import Flask
from flask_wtf.csrf import CsrfProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Initialize and configure Flask app
app = Flask(__name__)

# Dynamically choose config based on FLASK_ENV environment variable
if app.config["ENV"] == "development":
	app.config.from_object('config.DevelopmentConfig')
elif app.config["ENV"] == "testing":
	app.config.from_object('config.TestingConfig')
else:
	app.config.from_object('config.ProductionConfig')

# Trim excess whitespace when rendering with jinja2
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Add user directory
app.add_url_rule('/user/default/<path:filename>', endpoint='user',
                 view_func=app.send_static_file)

# Create database instance connected to webapp
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Secure web app forms against CSRF
csrf = CsrfProtect(app)

from app import views