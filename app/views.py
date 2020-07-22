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

# Internal imports
# from scripts import wn_customtrans as ctrans
# from scripts import configdata as config


# This is the route for the main page
@app.route("/")
def index():
	return render_template('index.html',
		title='CustomTrans')

# The following 4 routes are the routes for the 4 main page buttons
@app.route("/library")
def library():
	series=[
		{
            "abbr": "Dummy",
            "title": "This is a Sample Novel Title",
            "current": 1,
            "latest": 100,
            "code": "n7057gi"
        },
        {
            "abbr": "BocchiIdol",
            "title": "I'm the Best Idol in Japan",
            "current": 0,
            "latest": 45,
            "code": "n9946fx"
        },
        {
            "abbr": "FlagCrush",
            "title": "The Adventurer Contracted to the Strongest Deity Crushes Flags",
            "current": 145,
            "latest": 1206,
            "code": "n3404fh"
        },
        {
            "abbr": "CHJK",
            "title": "When My Childhood Friend Becomes JK",
            "current": 2,
            "latest": 28,
            "code": "n4893gi"
        },
        {
            "abbr": "WhiteRabbit",
            "title": "The Strongest Incompetent Reaches for the Top",
            "current": 1,
            "latest": 10,
            "code": "n0737ga"
        },
        {
            "abbr": "Surrounded",
            "title": "Surrounded By Four",
            "current": 50,
            "latest": 57,
            "code": "n9450ge"
        },
	]
	return render_template('library.html',
		title="Library",
		back_href=url_for('index'),
		series=series)

@app.route("/dictionaries")
def dictionaries():
	return "TODO: Implement Dictionaries Page"

@app.route("/tutorial")
def tutorial():
	return "TODO: Implement Tutorial Page"

@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"