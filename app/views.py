# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import json
from io import BytesIO
import os

# Flask imports
from flask import render_template
from flask import url_for
from flask import jsonify
from flask import request
from flask import send_file
from flask import flash
from flask import Response
from flask import abort

# Internal imports
from app import db
from app import app
from app import csrf

from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm
from app.forms import COMMON_DICT_ABBR

from app.models import *

from app.scripts import utils
from app.scripts import dictionary
from app.scripts import hostmanager
from app.scripts.custom_errors import *



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
	series = SeriesTable.query.order_by(SeriesTable.title).all();
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
		try:
			series_entry = utils.registerSeriesToDatabase(register_novel_form)
			if series_entry.latest_ch == 0:
				flash("Couldn't pull latest chapter for submitted series from host. \
					Try hitting \'Update\' later", "warning")
			flash("%s was successfully registered!" % series_entry.abbr, "success")
			return jsonify(status='ok')
		except CustomException as err:
			return jsonify(status='error', msg=str(err), severity=err.severity)


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
				try:
					num_updates = utils.updateSeries(series_entry)
				except:
					num_updates = -1
				data['updated'].append((series_entry.abbr, num_updates, series_entry.latest_ch))
				yield 'data: %s\n\n' % json.dumps(data)
	return Response(update_streamer(), mimetype="text/event-stream")


# Background route to process edit novel form
@app.route("/library/edit_novel/<series_code>", methods=["POST"])
def library_edit_novel(series_code):
	edit_novel_form = EditNovelForm()
	if edit_novel_form.validate_on_submit():
		series_entry = SeriesTable.query.filter_by(code=series_code).first()
		dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
		host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()

		new_title = edit_novel_form.title.data
		new_abbr  = edit_novel_form.abbr.data

		# Rename the associated dict according to new abbreviation
		fname_new = dictionary.generateDictFilename(
			edit_novel_form.abbr.data,
			host_entry.host_name,
			series_entry.code
		)
		dictionary.renameDictFile(dict_entry.fname, fname_new)
		# If the dict exists but is empty, repopulate it with the dictionary skeleton text
		dict_path = url_for('dict', filename=fname_new)[1:]
		if os.path.getsize(dict_path) == 0:
			host_manager = hostmanager.createManager(host_entry.host_type)
			createDictFile(fname_new, series_title, series_abbr, host_manager.generateSeriesUrl(series_code))
		dictionary.updateDictMetaHeader(fname_new, new_title, new_abbr)

		# Change the series entry itself
		series_entry.title = new_title
		series_entry.abbr = new_abbr
		db.session.commit()

		flash("Successfully applied changes!", "success")
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
			dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
			# Remove physical dict file
			dictionary.removeDictFile(dict_entry.fname)
			# Remove dict from database
			db.session.delete(dict_entry)
			db.session.commit()
			flash("Successfully removed dictionary associated with %s" % series_abbr, "success")

		# Remove series from database
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
	if series_entry is None:
		abort(404)

	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	host_mgr = hostmanager.createManager(host_entry.host_type)
	return render_template('series_toc.html',
		title=series_entry.abbr,
		back_href=url_for('library'),
		series=series_entry,
		series_url=host_mgr.generateSeriesUrl(series_entry.code))


# Route for updating a specific 'series'
@app.route("/library/<series_code>/update", methods=["POST"])
def library_series_update(series_code):
	series_entry = SeriesTable.query.filter_by(code=series_code).first()
	try:
		num_updates = utils.updateSeries(series_entry)
	except:
		return jsonify(status='error')

	return jsonify(status='ok', updates=num_updates)


# Route for removing a specific bookmark
@app.route("/library/<series_code>/bookmark/<ch>", methods=["POST"])
def library_series_toc_bookmark(series_code, ch):
	ch = int(ch)
	series_entry = SeriesTable.query.filter_by(code=series_code).first();
	if ch in series_entry.bookmarks:
		series_entry.bookmarks.remove(ch)
		db.session.add(series_entry)
		db.session.commit()
		return jsonify(status='ok', action='rmv_bookmark', target_ch=ch)

	series_entry.bookmarks.append(ch)
	db.session.add(series_entry)
	db.session.commit()
	return jsonify(status='ok', action='add_bookmark', target_ch=ch)


# Route for removing all bookmarks
@app.route("/library/<series_code>/bookmark/*", methods=["POST"])
def library_series_toc_bookmark_all(series_code):
	series_entry = SeriesTable.query.filter_by(code=series_code).first();
	series_entry.bookmarks = []
	db.session.add(series_entry)
	db.session.commit()
	return jsonify(status='ok')


# Route for a specific translated chapter 'ch' of 'series'
@app.route("/library/<series_code>/<ch>")
def library_series_chapter(series_code, ch):
	ch = int(ch)
	series_entry = SeriesTable.query.filter_by(code=series_code).first()
	if series_entry is None or ch < 1 or ch > series_entry.latest_ch:
		abort(404)

	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	host_mgr = hostmanager.createManager(host_entry.host_type)
	if host_entry.host_lang == hostmanager.Language.JP:
		dummy_text = u"ダミー"
	elif host_entry.host_lang == hostmanager.Language.CN:
		dummy_text = u"假"

	try:
		chapter_data = utils.customTrans(series_entry, ch)
	except CustomException as err:
		flash(str(err), "danger")
		return render_template("chapter.html",
			title="%s %d" % (series_entry.abbr, ch),
			default_theme="dark",
			series=series_entry,
			ch=ch,
			dummy_text=dummy_text,
			series_url=host_mgr.generateSeriesUrl(series_entry.code),
			chapter_url=host_mgr.generateChapterUrl(series_entry.code, ch))

	return render_template("chapter.html",
		title="%s %d" % (series_entry.abbr, ch),
		default_theme="dark",
		series=series_entry,
		ch=ch,
		dummy_text=dummy_text,
		series_url=host_mgr.generateSeriesUrl(series_entry.code),
		chapter_url=host_mgr.generateChapterUrl(series_entry.code, ch),
		chapter_data=chapter_data)


# Route for Dictionaries view
@app.route("/dictionaries")
def dictionaries():
	series = SeriesTable.query.all()
	dictionaries = []
	for entry in series:
		dict_entry = DictionaryTable.query.filter_by(id=entry.dict_id).first()
		dictionaries.append({
			"abbr": entry.abbr,
			"fname": dict_entry.fname,
			"enabled": dict_entry.enabled
		})
	dictionaries = sorted(dictionaries, key=lambda k: k['abbr'])

	# Add common_dict
	dict_entry = DictionaryTable.query.filter_by(fname=dictionary.COMMON_DICT_FNAME).first()
	dictionaries.insert(0, {
		"abbr": COMMON_DICT_ABBR,
		"fname": dict_entry.fname,
		"enabled": dict_entry.enabled
	})

	return render_template("dictionary.html",
		title="Dictionary",
		dictionaries=dictionaries,
		back_href=url_for('index'))


# Route for enabling/disabling dictionaries
@app.route("/dictionaries/toggle/<dict_abbr>", methods=["POST"])
def dictionaries_toggle_entry(dict_abbr):
	if dict_abbr == "Common":
		dict_entry = DictionaryTable.query.filter_by(fname=dictionary.COMMON_DICT_FNAME).first()
	else:
		series_entry = SeriesTable.query.filter_by(abbr=dict_abbr).first()
		dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
	dict_entry.enabled = not dict_entry.enabled
	db.session.add(dict_entry)
	db.session.commit()

	data = {
		"status": "ok",
		"toggle": int(dict_entry.enabled)
	}
	return jsonify(data)

# @app.route("/dictionaries/upload/<series>", methods=["POST"])
# def dictionaries_upload_dict(series):
# 	dict_file = request.files['inputFile']

# 	db_file = DictionaryTable(name=dict_file.filename, data=dict_file.read())
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
	return render_template('tutorial.html',
		title="Tutorial")


# Route for user settings
@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"