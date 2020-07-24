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
from flask import send_file

# Internal imports
from app import app
from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm
from app.models import SeriesTable
from app.models import DictionaryFile

# Other imports
import json
from io import BytesIO

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
@app.route("/library")
def library():
	register_novel_form = RegisterNovelForm()
	edit_novel_form = EditNovelForm()
	remove_novel_form = RemoveNovelForm()

	return render_template('library.html',
		title="Library",
		back_href=url_for('index'),
		series=series,
		reg_form=register_novel_form,
		edit_form=edit_novel_form,
		rmv_form=remove_novel_form)

# Background route to process register novel form
@app.route("/library/register_novel", methods=["POST"])
def library_register_novel():
	register_novel_form = RegisterNovelForm()
	if register_novel_form.validate_on_submit():
		return jsonify(status='ok')

	data = json.dumps(register_novel_form.errors, ensure_ascii=False)
	return jsonify(data)

# Background route to process edit novel form
@app.route("/library/edit_novel", methods=["POST"])
def library_edit_novel():
	edit_novel_form = EditNovelForm()
	if edit_novel_form.validate_on_submit():
		return jsonify(status='ok')

	data = json.dumps(edit_novel_form.errors, ensure_ascii=False)
	return jsonify(data)

# Background route to process remove novel form
@app.route("/library/remove_novel", methods=["POST"])
def library_remove_novel():
	remove_novel_form = RemoveNovelForm()
	if remove_novel_form.validate_on_submit():
		if remove_novel_form.opt_keep_dict:
			print("Kept dict and removed the series")
		else:
			print("Removed the series and dict")
		return jsonify(status='ok')

	data = json.dumps(remove_novel_form.errors, ensure_ascii=False)
	return jsonify(data)

# Route for the table of content for given 'series'
@app.route("/library/<series>")
def library_series_toc(series):
	return "Displaying Table of Contents for %s" % series

# Route for a specific translated chapter 'ch' of 'series'
@app.route("/library/<series>/<ch>")
def library_series_chapter(series, ch):
	return "Displaying %s chapter %s" % (series, ch)


@app.route("/dictionaries")
def dictionaries():
	return "TODO: Implement Dictionaries Page"

# @app.route("/dictionaries/upload/<series>", methods=["POST"])
# def dictionaries_upload_dict(series):
# 	dict_file = request.files['inputFile']

# 	db_file = DictionaryFile(name=dict_file.filename, data=dict_file.read())
# 	db.session.add(db_file)
# 	db.session.commit()

# 	return 'Saved %s to the database!' % dict_file.filename

# @app.route("/dictionaries/download/<series>", methods=["POST"])
# def dictionaries_download_dict(series):
# 	dict_file = Query SQLAlchemy
#	fname = "Blah.dict"
# 	return send_file(BytesIO(dict_file.file_data), attachment_filename=fname, as_attachment=True)


@app.route("/tutorial")
def tutorial():
	register_novel_form = RegisterNovelForm()
	return render_template('tutorial.html',
		title="Tutorial",
		reg_form=register_novel_form)

@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"