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
from flask import flash
from flask import Response

# Internal imports
from app import db
from app import app
from app import csrf
from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm
from app.models import SeriesTable
from app.models import DictionariesTable
from app.models import HostTable
from app.scripts import utils

# Other imports
import json
from io import BytesIO




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

	# Fetch series from database
	series = SeriesTable.query.all()
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
		series_entry = utils.registerSeriesToDatabase(register_novel_form)
		if series_entry.latest_ch == 0:
			flash("Couldn't pull latest chapter for submitted series from host. \
				Try hitting \'Update\' later", "warning")
		flash("%s was successfully registered!" % series_entry.abbr, "success")
		return jsonify(status='ok')

	data = json.dumps(register_novel_form.errors, ensure_ascii=False)
	return jsonify(data)


# Background route to process update
@app.route("/library/update")
def library_update():
	def update_streamer():
		# Since context is lost in request, test_request_context() is needed to preserve it
		with app.test_request_context("/library"):
			data = {}
			all_series = SeriesTable.query.all()
			data['num_series'] = len(all_series)
			data['updated'] = []
			for index in range(0, len(all_series)):
				series_entry = all_series[index]
				num_updates = utils.updateSeries(series_entry)
				data['updated'].append((series_entry.abbr, num_updates, series_entry.latest_ch))
				yield 'data: %s\n\n' % json.dumps(data)
	return Response(update_streamer(), mimetype="text/event-stream")


# Background route to process edit novel form
@app.route("/library/edit_novel/<series_code>", methods=["POST"])
def library_edit_novel(series_code):
	edit_novel_form = EditNovelForm()
	if edit_novel_form.validate_on_submit():
		series_entry = SeriesTable.query.filter_by(code=series_code).first()
		series_entry.title = edit_novel_form.title.data
		series_entry.abbr = edit_novel_form.abbr.data
		db.session.commit()
		flash("Changes have been applied!", "success")
		return jsonify(status='ok')

	data = json.dumps(edit_novel_form.errors, ensure_ascii=False)
	return jsonify(data)


# Background route to process remove novel form
@app.route("/library/remove_novel/<series_code>", methods=["POST"])
def library_remove_novel(series_code):
	remove_novel_form = RemoveNovelForm()
	if remove_novel_form.validate_on_submit():
		series_entry = SeriesTable.query.filter_by(code=series_code).first()
		series_abbr = series_entry.abbr
		if not remove_novel_form.opt_keep_dict.data:
			dict_entry = DictionariesTable.query.filter_by(id=series_entry.dict_id).first()
			db.session.delete(dict_entry)
			flash("Removed dictionary associated with %s" % series_abbr, "success")
		db.session.delete(series_entry)
		db.session.commit()

		flash("Successfully removed %s!" % series_abbr, "success")
		return jsonify(status='ok')

	data = json.dumps(remove_novel_form.errors, ensure_ascii=False)
	return jsonify(data)


# Route for the table of content for given 'series'
@app.route("/library/<series_code>")
def library_series_toc(series_code):
	series_entry = SeriesTable.query.filter_by(code=series_code).first()
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	series_host_url = host_entry.host_url + series_entry.code
	return render_template('series_toc.html',
		title=series_entry.abbr,
		back_href=url_for('library'),
		series=series_entry,
		series_host_url=series_host_url)

#@csrf.exempt
@app.route("/library/<series_code>/bookmark/<ch>", methods=["POST"])
def library_series_toc_bookmark(series_code, ch):
	ch = int(ch)
	series_entry = SeriesTable.query.filter_by(code=series_code).first();
	if(ch in series_entry.bookmarks):
		series_entry.bookmarks.remove(ch)
		db.session.add(series_entry)
		db.session.commit()
		return jsonify(status='ok', action='rmv_bookmark', target_ch=ch)

	series_entry.bookmarks.append(ch)
	db.session.add(series_entry)
	db.session.commit()
	return jsonify(status='ok', action='add_bookmark', target_ch=ch)

# Route for a specific translated chapter 'ch' of 'series'
@app.route("/library/<series_code>/<ch>")
def library_series_chapter(series_code, ch):
	series_entry = SeriesTable.query.filter_by(code=series_code).first()
	return "Displaying %s chapter %s" % (series_entry.title, ch)


# Route for Dictionaries view
@app.route("/dictionaries")
def dictionaries():
	return "TODO: Implement Dictionaries Page"



# @app.route("/dictionaries/upload/<series>", methods=["POST"])
# def dictionaries_upload_dict(series):
# 	dict_file = request.files['inputFile']

# 	db_file = DictionariesTable(name=dict_file.filename, data=dict_file.read())
# 	db.session.add(db_file)
# 	db.session.commit()

# 	return 'Saved %s to the database!' % dict_file.filename



# @app.route("/dictionaries/download/<series>", methods=["POST"])
# def dictionaries_download_dict(series):
# 	dict_file = Query SQLAlchemy
#	fname = "Blah.dict"
# 	return send_file(BytesIO(dict_file.file_data), attachment_filename=fname, as_attachment=True)


# Route for Tutorial page
@app.route("/tutorial")
def tutorial():
	register_novel_form = RegisterNovelForm()
	return render_template('tutorial.html',
		title="Tutorial",
		reg_form=register_novel_form)


# Route for user settings
@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"