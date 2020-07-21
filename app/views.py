#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Flask imports
from flask import render_template
from flask import url_for
from app import app

# This is the route for the main page
@app.route("/")
def index():
	return render_template('index.html', title='Index Page')

# The following 4 routes are the routes for the 4 main page buttons
@app.route("/library")
def library():
	return "TODO: Implement Library Page"

@app.route("/dictionaries")
def dictionaries():
	return "TODO: Implement Dictionaries Page"

@app.route("/tutorial")
def tutorial():
	return "TODO: Implement Tutorial Page"

@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"