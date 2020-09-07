# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import os
import json
import zipfile
import io

# Flask imports
from flask import render_template
from flask import url_for
from flask import jsonify
from flask import request
from flask import redirect
from flask import flash
from flask import Response
from flask import abort
from flask import send_file
from flask import send_from_directory

# Internal imports
from app import db
from app import app
from app import csrf

from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm

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

# Custom error handlers
@app.errorhandler(404)
def error_404(error):
	hdr = '''<strong>Ummm...</strong> The page you requested does not
		exist'''
	desc = '''Perhaps you followed a bad link. Or maybe this is a series
		sepcific page for a series that\'s no longer in your Library?'''
	return render_template('error_page.html',
		title='Error 404',
		err_img=url_for('static', filename="error_404_img.gif"),
		err_code=404,
		err_msg_header=hdr,
		err_msg_description=desc)

# Custom error handlers
@app.errorhandler(500)
def error_500(error):
	hdr = '''<strong>Whoops!</strong> Server error. Yeah this one\'s on me...'''
	desc = '''Looks like something caused the server side to error out. It's
		not a you-problem though, it's a me-problem. Accept this sliding dogeza!'''
	return render_template('error_page.html',
		title='Error 500',
		err_img=url_for('static', filename="error_500_img.gif"),
		err_code=500,
		err_msg_header=hdr,
		err_msg_description=desc)

# The following 4 routes are the routes for the 4 main page buttons
@app.route("/library")
def library():
	register_novel_form = RegisterNovelForm()
	edit_novel_form = EditNovelForm()
	remove_novel_form = RemoveNovelForm()

	# Fetch series from database
	series = SeriesTable.query.order_by(SeriesTable.title).all();
	# Add additional host info
	for entry in series:
		host_entry = HostTable.query.filter_by(id=entry.host_id).first()
		entry.__dict__["host"] = host_entry.host_name
		entry.__dict__["lang"] = lang = Language.to_string(host_entry.host_lang)
		dict_entry = DictionaryTable.query.filter_by(id=entry.dict_id).first()
		entry.__dict__["dict_fname"] = dict_entry.fname
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
				flash("%s Couldn't pull latest chapter for %s from host. \
					Try hitting \'Update\' later" % (WARNING_BOLD, strong(series_entry.abbr)),
					"warning")
			msg = "%s %s was successfully registered!" % (SUCCESS_BOLD, strong(series_entry.abbr))
			flash(msg, "success")
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
		import pdb; pdb.set_trace()
		series_entry = SeriesTable.query.filter_by(code=series_code).first()
		dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
		host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
		host_manager = hostmanager.createManager(host_entry.host_type)

		new_title = edit_novel_form.title.data
		new_abbr  = edit_novel_form.abbr.data
		fname_new = dictionary.generateDictFilename(
			edit_novel_form.abbr.data,
			host_entry.host_name,
			series_entry.code
		)
		dict_path_old = os.path.join(app.config['DICTIONARIES_PATH'], dict_entry.fname)
		dict_path_new = os.path.join(app.config['DICTIONARIES_PATH'], fname_new)

		# First check if the dicitonary file exists, create it if necessary
		if not os.path.exists(dict_path_old):
			dictionary.createDictFile(fname_new,
				new_title,
				new_abbr,
				host_manager.generateSeriesUrl(series_code))
		# It exists so reprocess it
		else:
			# Rename the associated dict according to new abbreviation
			dictionary.renameDictFile(dict_entry.fname, fname_new)
			# If the dict exists but is empty, repopulate it with the dictionary skeleton text
			if os.path.getsize(dict_path_new) == 0:
				dictionary.createDictFile(fname_new,
					new_title,
					new_abbr,
					host_manager.generateSeriesUrl(series_code))
			# Otherwise, just update the meta
			else:
				dictionary.updateDictMetaHeader(fname_new, new_title, new_abbr)

		# Change the series entry itself
		series_entry.title = new_title
		series_entry.abbr = new_abbr
		dict_entry.fname = fname_new
		db.session.commit()

		flash("%s Your changes have been applied!" % SUCCESS_BOLD, "success")
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
			flash("%s Removed the following dictionary: %s" % (SUCCESS_BOLD, mono(dict_entry.fname)),
				"success")

		# Remove series from database
		db.session.delete(series_entry)
		db.session.commit()

		flash("%s Removed %s!" % (SUCCESS_BOLD, strong(series_abbr)), "success")
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
	if ch > series_entry.latest_ch:
		# Can't set a current chapter if it's greater than the latest chapter
		return jsonify(status='illegal_chapter_abort', target_ch=ch)

	if ch in series_entry.bookmarks:
		series_entry.bookmarks.remove(ch)
		db.session.commit()
		return jsonify(status='ok', action='rmv_bookmark', target_ch=ch)

	series_entry.bookmarks.append(ch)
	db.session.commit()
	return jsonify(status='ok', action='add_bookmark', target_ch=ch)


# Route for manual reseting of the current chapter for a given series
@app.route("/library/<series_code>/setcurrent/<ch>", methods=["POST"])
def library_series_toc_setcurrent(series_code, ch):
	ch = int(ch)
	series_entry = SeriesTable.query.filter_by(code=series_code).first();
	if ch > series_entry.latest_ch:
		# Can't set a current chapter if it's greater than the latest chapter
		return jsonify(status='illegal_chapter_abort', target_ch=ch)

	if ch == series_entry.current_ch:
		# Ignore to set current chapter as current chapter
		return jsonify(status='trivial_abort', target_ch=ch)

	series_entry.current_ch = ch
	db.session.commit()
	return jsonify(status='ok', target_ch=ch)


# Route for removing all bookmarks
@app.route("/library/<series_code>/bookmark/*", methods=["POST"])
def library_series_toc_bookmark_all(series_code):
	series_entry = SeriesTable.query.filter_by(code=series_code).first();
	series_entry.bookmarks = []
	db.session.commit()
	return jsonify(status='ok')


# Route for a specific translated chapter 'ch' of 'series'
@app.route("/library/<series_code>/<ch>")
def library_series_chapter(series_code, ch):
	ch = int(ch)
	series_entry = SeriesTable.query.filter_by(code=series_code).first()
	if series_entry is None or ch < 1 or ch > series_entry.latest_ch:
		abort(404)

	back_href = url_for('library_series_toc', series_code=series_code)

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
			back_href=back_href,
			default_theme="dark",
			series=series_entry,
			ch=ch,
			dummy_text=dummy_text,
			series_url=host_mgr.generateSeriesUrl(series_entry.code),
			chapter_url=host_mgr.generateChapterUrl(series_entry.code, ch))

	return render_template("chapter.html",
		title="%s %d" % (series_entry.abbr, ch),
		back_href=back_href,
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
			"id": dict_entry.id,
			"abbr": entry.abbr,
			"fname": dict_entry.fname,
			"enabled": dict_entry.enabled
		})
	dictionaries = sorted(dictionaries, key=lambda k: k['abbr'])

	# Add common_dict
	dict_entry = DictionaryTable.query.filter_by(fname=dictionary.COMMON_DICT_FNAME).first()
	dictionaries.insert(0, {
		"id": dict_entry.id,
		"abbr": dictionary.COMMON_DICT_ABBR,
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
	try:
		if dict_abbr == "Common":
			dict_entry = DictionaryTable.query.filter_by(fname=dictionary.COMMON_DICT_FNAME).first()
		else:
			series_entry = SeriesTable.query.filter_by(abbr=dict_abbr).first()
			if series_entry is None:
				raise SeriesEntryDNEException(dict_abbr)
			dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
	except CustomException as err:
		return jsonify(status='series_nf', msg=str(err), severity=err.severity)

	dict_entry.enabled = not dict_entry.enabled
	db.session.commit()

	data = {
		"status": "ok",
		"toggle": dict_entry.enabled
	}
	return jsonify(data)


# Route for toggle all dictionaries to the given enable status
@app.route("/dictionaries/toggleall/<enable>", methods=["POST"])
def dictionaries_toggleall(enable):
	master_toggle = True if enable == 'on' else False
	for dict_entry in DictionaryTable.query.all():
		dict_entry.enabled = master_toggle
		db.session.commit()

	data = {
		"status": "ok",
		"toggle": master_toggle
	}
	return jsonify(data)


@app.route("/dictionaries/upload/<dict_fname>", methods=["POST"])
def dictionaries_upload_dict(dict_fname):
	if request.files:
		try:
			uploaded_dict_file = request.files['uploaded_dict_file']
			dict_entry = DictionaryTable.query.filter_by(fname=dict_fname).first()
			if dict_entry is None:
				raise DictEntryDNEException(dict_fname)

			# File size constraint
			if int(request.cookies.get("filesize")) > app.config['MAX_DICT_FILESIZE']:
				fsize_mb = app.config['MAX_DICT_FILESIZE'] / 1024 / 1024
				raise FileTooLargeException("%sMB" % int(fsize_mb))

			# File extension constraint
			ext = utils.getFileExtension(uploaded_dict_file.filename)
			if ext is None:
				raise InvalidFilenameException(uploaded_dict_file.filename)
			elif not ext.upper() in app.config['ALLOWED_DICT_EXTENSIONS']:
				raise InvalidDictFileExtensionException(ext)

			# Validation stage passed. Save the file on the server
			uploaded_dict_file.save(
				os.path.join(app.config['DICTIONARIES_PATH'], dict_entry.fname))

			# Flash success
			flash("%s File has successfully uploaded and replaced %s" % \
				(SUCCESS_BOLD, mono(dict_entry.fname)),
				"success")
		except CustomException as err:
			flash(str(err), err.severity)
		except Exception as err:
			flash("%s Encountered an unexpected server-side error" % CRITICAL_BOLD,
				"danger")
	else:
		flash("%s File upload failed" % CRITICAL, "danger")

	return redirect(url_for('dictionaries'))


# Route for downloading a given .dict file
@app.route("/dictionaries/download/<dict_fname>", methods=["POST"])
def dictionaries_download_dict(dict_fname):
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	if not os.path.exists(dict_path):
		return jsonify({"status": "dict_dne_abort"})
	try:
		return send_from_directory(app.config['DICTIONARIES_PATH'],
			filename=dict_fname,
			as_attachment=True)
	except Exception as err:
		return jsonify({"status": "dict_download_error"})


# Route for downloading all dict files in user/dicts
@app.route("/dictionaries/downloadall")
def dictionaries_download_all():
	#import pdb; pdb.set_trace()
	data = io.BytesIO()
	with zipfile.ZipFile(data, mode='w', compression=zipfile.ZIP_DEFLATED) as dict_zip:
		for (root, _, files) in os.walk(app.config['DICTIONARIES_PATH']):
			for dict_fname in files:
				dict_path = os.path.join(root, dict_fname)
				dict_zip.write(dict_path, arcname=dict_fname)

	data.seek(0)
	return send_file(data,
		mimetype="application/zip",
		as_attachment=True,
		attachment_filename='wnct_dictionaries.zip')


# Route for downloading all dict files in user/dicts
@app.route("/dictionaries/edit/<dict_fname>")
def dictionaries_edit(dict_fname):
	if utils.spliceDictName(dict_fname):
		if DictionaryTable.query.filter_by(fname=dict_fname).first() is None:
			abort(404)

		(series_abbr, host_name, series_code) = utils.spliceDictName(dict_fname)
		host_entry = HostTable.query.filter_by(host_name=host_name).first()
		if host_entry is None:
			abort(404)
		host_manager = hostmanager.createManager(host_entry.host_type)
		series_entry = SeriesTable.query.filter_by(host_id=host_entry.id, code=series_code).first()
		if series_entry is None:
			abort(404)

		series_title = series_entry.title
		series_abbr = series_entry.abbr
		series_url = host_manager.generateSeriesUrl(series_code)

	elif dict_fname == dictionary.COMMON_DICT_FNAME:
		series_title = dictionary.COMMON_DICT_TITLE
		series_abbr = dictionary.COMMON_DICT_ABBR
		series_url = "N/A"
	else:
		return abort(404)

	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	if not os.path.exists(dict_path):
		dictionary.createDictFile(dict_fname, series_title, series_abbr, series_url)
		flash("Dictionary file %s was newly created" % mono(dict_fname), "success")
	elif os.path.getsize(dict_path) == 0:
		dictionary.createDictFile(dict_fname, series_title, series_abbr, series_url)
		flash("Dictionary file %s was found empty. The header metadata was reinitialized" % \
			mono(dict_fname), "success")

	dict_content = ""
	try:
		with io.open(dict_path, mode='r', encoding='utf8') as dict_file:
			dict_content = dict_file.read()
	except Exception as err:
		flash("%s Ran into an issue opening the file %s" % \
			(WARNING_BOLD, mono(dict_fname)), "warning")

	return render_template("dictionary_edit.html",
		title="Edit %s" % series_abbr,
		back_href=url_for('dictionaries'),
		series_abbr=series_abbr,
		dict_fname=dict_fname,
		dict_content=dict_content)


# Route for Tutorial page
@app.route("/tutorial")
def tutorial():
	return render_template('tutorial.html',
		title="Tutorial")


# Route for user settings
@app.route("/settings")
def settings():
	return "TODO: Implement Settings Page"