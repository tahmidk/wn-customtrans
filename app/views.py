#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Flask imports
from flask import render_template
from flask import url_for
from flask import jsonify
from flask import request

# Internal imports
from app import app
from app.forms import RegisterNovelForm

# Other imports
import json

# Static database to temporarily use
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

# This is the route for the main page
@app.route("/")
def index():
	return render_template('index.html',
		title='CustomTrans')

# The following 4 routes are the routes for the 4 main page buttons
@app.route("/library", methods=["GET", "POST"])
def library():
	register_novel_form = RegisterNovelForm()
	if request.method == 'POST':
		#import pdb; pdb.set_trace()
		if register_novel_form.validate_on_submit():
			return jsonify(status='ok')
		else:
			data = json.dumps(register_novel_form.errors, ensure_ascii=False)
			return jsonify(data)

	return render_template('library.html',
		title="Library",
		back_href=url_for('index'),
		series=series,
		reg_form=register_novel_form)

@app.route("/dictionaries", methods=["GET", "POST"])
def dictionaries():
	return "TODO: Implement Dictionaries Page"

@app.route("/tutorial")
def tutorial():
	register_novel_form = RegisterNovelForm()
	return render_template('tutorial.html',
		title="Tutorial",
		reg_form=register_novel_form)

@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"