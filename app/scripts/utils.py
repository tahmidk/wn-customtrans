#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import os
import io
import ssl
import re
import json

from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError

# Flask imports
from flask import url_for

# Internal imports
from app import app
from app import db

from app.forms import *
from app.models import *

from app.scripts.hostmanager import *
from app.scripts.custom_errors import *
from app.scripts.dictionary import *



def fetchHtml(url, lang):
	"""-------------------------------------------------------------------
		Function:		[fetchHtml]
		Description:	Tries to prompt a response url and return the received
						HTML content as a UTF-8 decoded string
		Input:
		  [url]			The url to make the request to
		  [lang]		The page's language (Language Enum)
		Return: 		The HTML content of the given website address
		------------------------------------------------------------------
	"""
	try:
		headers = { 'User-Agent' : 'Mozilla/5.0' }
		request = Request(url, None, headers)
		response = urlopen(request, context=ssl._create_unverified_context())
	except:
		raise HtmlFetchException(url)

	# Read and decode the response according to series language
	source = response.read()
	if lang == Language.JP:
		data = source.decode('utf8')
	elif lang == Language.CN:
		data = source.decode('gbk')

	return data

def getLatestChapter(series_code, host_entry):
	"""-------------------------------------------------------------------
		Function:		[getLatestChapter]
		Description:	Fetches the latest chapter directly from the series's host
		Input:
		  [series_code]	The identifying series code
		  [host_entry] 	The HostTable entry associated with this series
		Return:			Latest chapter number
		------------------------------------------------------------------
	"""
	source_url = host_entry.host_url + series_code
	source_html = fetchHtml(source_url, host_entry.host_lang)
	html_parser = createManager(host_entry.host_type)
	res = html_parser.getLatestChapter(source_html)

	return res

def getFileExtension(filename):
	"""-------------------------------------------------------------------
		Function:		[getFileExtension]
		Description:	Fetches the latest chapter directly from the series's host
		Input:
		  [series_code]	The identifying series code
		  [host_entry] 	The HostTable entry associated with this series
		Return:			Latest chapter number
		------------------------------------------------------------------
	"""
	if not '.' in filename:
		return None

	return filename.split('.')[-1]

def registerSeriesToDatabase(reg_form):
	"""-------------------------------------------------------------------
		Function:		[registerSeriesToDatabase]
		Description:	Pushes user series info to database initializing
						the associated dictionary as well
		Input:
		  [reg_form] 	The Flask novel registration form to process
		Return:			The new series as a db Table entry
						None if error encountered
		------------------------------------------------------------------
	"""
	# Rip relevant information
	series_title = reg_form.title.data.strip()
	series_abbr = reg_form.abbr.data.strip()
	series_code = reg_form.series_code.data.strip()

	host_entry = reg_form.series_host.data
	dict_fname = generateDictFilename(series_abbr, host_entry.host_name, series_code)
	dict_entry = None

	# Check for preexisting dictionary if this series is being re-registered
	for entry in DictionaryTable.query.all():
		dict_info = spliceDictName(entry.fname)
		if dict_info is not None:
			(_, host, code) = dict_info
			if host == host_entry.host_name and code == series_code:
				dict_entry = entry
				if dict_entry.fname != dict_fname:
					renameDictFile(dict_entry.fname, dict_fname)
					dict_entry.fname = dict_fname
				break

	# If an existing dictionary is not found, make a new entry
	if dict_entry is None:
		dict_entry = DictionaryTable(
			fname=dict_fname,
		)
	db.session.add(dict_entry)
	db.session.commit()

	# Check the physical file,
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	if not os.path.exists(dict_path):
		# First traverse the dict files to see if there is a dict file with the same host-code combination
		# This implies the user has registered and removed this series before with the preserve dictionary
		# option enabled and is currently trying to reregister that same series
		dict_initialized = False
		for dict_file in os.listdir(app.config['DICTIONARIES_PATH']):
			if os.path.isfile(os.path.join(app.config['DICTIONARIES_PATH'], dict_file)):
				info = spliceDictName(dict_file)
				if info is not None:
					(_, host, code) = info
					if host == host_entry.host_name and code == series_code:
						# Found a dict file with matching host+code, rename it and use it for this series dict
						renameDictFile(dict_file, dict_fname)
						updateDictMetaHeader(dict_fname, series_title, series_abbr)
						dict_initialized = True
						break

		# Dict with this host+code combination wasn't found, create a new one from scratch
		if not dict_initialized:
			host_manager = createManager(host_entry.host_type)
			createDictFile(dict_fname, series_title, series_abbr, host_manager.generateSeriesUrl(series_code))

	# If the dict exists but is empty, repopulate it with the dictionary skeleton text
	if os.path.getsize(dict_path) == 0:
		host_manager = createManager(host_entry.host_type)
		createDictFile(dict_fname, series_title, series_abbr, host_manager.generateSeriesUrl(series_code))

	# Finally build the table for the series
	series_entry = SeriesTable(
		code=series_code,
		title=series_title,
		abbr=series_abbr,
		current_ch=0,
		latest_ch=getLatestChapter(series_code, host_entry),
		bookmarks=[],
		dict_id=dict_entry.id,
		host_id=host_entry.id,
	)
	db.session.add(series_entry)
	db.session.commit()

	return series_entry

def updateSeries(series_entry):
	"""-------------------------------------------------------------------
		Function:		[updateSeries]
		Description:	Updates a specific series
		Input:
		  [reg_form] 	The Flask novel registration form to process
		Return:			Number of chapter updates on success
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	latest = getLatestChapter(series_entry.code, host_entry)
	ret = latest - series_entry.latest_ch;
	series_entry.latest_ch = latest
	db.session.commit()

	return ret

def applyDictionaryToContent(content, series_dict):
	"""-------------------------------------------------------------------
		Function:		[applyDictionaryToContent]
		Description:	Applies the designated series dictionary to the given
						story content
		Input:
		  [series_abbr] The abbreviation of the series
		  [content]		Formatted chapter content gotten from hostmanager
		Return: 		None, mutates content
		------------------------------------------------------------------
	"""
	# Helper function that generates a placeholder element with the given id
	def generatePlaceholder(id):
		return "<span class=\"placeholder\" id=\"p%d\">placeholder</span>" % id

	# Preprocess line using dictionary entities
	series_dict_list = list(series_dict.items())
	for i in range(0, len(content)):
		if content[i]["type"] == "text":
			for j in range(0, len(series_dict)):
				(def_raw, (def_trans, def_comment)) = series_dict_list[j]
				if def_raw in content[i]["text"]:
					content[i]["text"] = content[i]["text"].replace(def_raw, generatePlaceholder(j+1))

def addHonorificToDatabase(honorific_add_form):
	"""-------------------------------------------------------------------
		Function:		[addHonorificToDatabase]
		Description:	Adds the honorific indicated in the form to the database
		Input:
		  [honorific_add_form] The submitted Honorific Add form
		Return: 		Returns new honorific entry on success, None otherwise
		------------------------------------------------------------------
	"""
	# Rip relevant information
	lang = Language(honorific_add_form.lang.data)
	hraw = honorific_add_form.hraw.data.strip()
	htrans = honorific_add_form.htrans.data.strip()

	affix = HonorificAffix(honorific_add_form.affix.data)
	opt_with_dash = honorific_add_form.opt_with_dash.data
	opt_standalone = honorific_add_form.opt_standalone.data

	honorific_entry = HonorificsTable(
		lang=lang,
		raw=hraw,
		trans=htrans,
		affix=affix,
		opt_with_dash=opt_with_dash,
		opt_standalone=opt_standalone,
		enabled=True
	)
	db.session.add(honorific_entry)
	db.session.commit()

	return honorific_entry

def editHonorific(hon_id, honorific_edit_form):
	"""-------------------------------------------------------------------
		Function:		[addHonorificToDatabase]
		Description:	Changes the data of the honorific with the designated id
						in the database
		Input:
		  [honorific_edit_form] The submitted Honorific Edit form
		Return: 		Returns edited honorific entry on success, None otherwise
		------------------------------------------------------------------
	"""
	try:
		hon_entry = HonorificsTable.query.filter_by(id=hon_id).first()
		if hon_entry is None:
			raise HonorificDNEException(hon_id)

		# Apply edits
		hon_entry.lang = Language(honorific_edit_form.lang.data)
		hon_entry.raw = honorific_edit_form.hraw.data.strip()
		hon_entry.trans = honorific_edit_form.htrans.data.strip()
		hon_entry.affix = HonorificAffix(honorific_edit_form.affix.data)
		hon_entry.opt_with_dash = honorific_edit_form.opt_with_dash.data
		hon_entry.opt_standalone = honorific_edit_form.opt_standalone.data

		db.session.commit()
		return hon_entry
	except:
		return None


def customTrans(series_entry, ch):
	"""-------------------------------------------------------------------
		Function:		[customTrans]
		Description:	Generates the pre-processed data necessary to populate
						the chapter template
		Input:
		  [series_entry]The series db entry to generate the customtrans chapter for
		  [ch]			The integer indicating the chapter number
		Return: 		Returns a tuple consisting of the chapter data and
						the series dictionary structure
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()

	# First fetch the html
	host_manager = createManager(host_entry.host_type)
	chapter_url = host_manager.generateChapterUrl(series_entry.code, ch)
	chapter_html = fetchHtml(chapter_url, host_entry.host_lang)

	# Parse out relevant content from the website source code
	chapter_content = host_manager.parseChapterContent(chapter_html)
	series_dict = initSeriesDict(series_entry.abbr)
	applyDictionaryToContent(chapter_content, series_dict)

	# Done, pack all the data together and return it to the client
	chapter_data = {
		"title": 		next(datum for datum in chapter_content if datum['ltype'] == LType.TITLE),
		"prescript": 	[datum for datum in chapter_content if datum['ltype'] == LType.PRESCRIPT],
		"main": 		[datum for datum in chapter_content if datum['ltype'] == LType.MAIN],
		"postscript": 	[datum for datum in chapter_content if datum['ltype'] == LType.POSTSCRIPT],
		"dictionary":	[{"trans":t, "comment":c} for (_, (t, c)) in series_dict.items()]
	}
	return chapter_data

def seedSeries(series_json_path, mode='append'):
	"""-------------------------------------------------------------------
		Function:		[seedSeries]
		Description:	Seeds the SeriesTable on the database using series found
						in the given json file
		Input:
		  [series_json_path] Path to the json file containing the series to seed
		  [mode]		If 'overwrite', drops SeriesTable data before seeding
		  				Default 'append' will append to SeriesTable
		Return:			None, reseeds HostTable

		PRECONDITION: 	HostTable contains a row for the hosts referred to by the
						series in the given json
		------------------------------------------------------------------
	"""
	print("Seeding database's SeriesTable and DictionaryTable from \'%s\' in \'%s\' mode" %
		(series_json_path, mode))

	if mode == 'overwrite':
		SeriesTable.__table__.drop(db.engine)
		DictionaryTable.__table__.drop(db.engine)
		db.metadata.create_all(db.engine, tables=[
			SeriesTable.__table__,
			DictionaryTable.__table__])

		# Add back the common dictionary
		dict_entry = DictionaryTable(
			fname="common_dict.dict",
		)
		db.session.add(dict_entry)
		db.session.commit()


	# Populate database from json
	with open(series_json_path, mode='r') as series_json:
		series_content = json.loads(series_json.read())
		for entry in series_content['series']:
			host_entry = HostTable.query.filter_by(host_type=Host.to_enum(entry['host'])).first();
			# Submit dictionary to database
			dict_fname = generateDictFilename(entry['abbr'], host_entry.host_name, entry['code'])
			dict_entry = DictionaryTable(
				fname=dict_fname,
			)
			db.session.add(dict_entry)
			db.session.commit()

			# Create series entry in database
			series_entry = SeriesTable(
				code=entry['code'],
				title=entry['title'],
				abbr=entry['abbr'],
				current_ch=entry['current'],
				latest_ch=entry['latest'],
				bookmarks=entry['bookmarks'],
				dict_id=dict_entry.id,
				host_id=host_entry.id
			)
			db.session.add(series_entry)
		db.session.commit()

def seedHosts(hosts_json_path, mode='append'):
	"""-------------------------------------------------------------------
		Function:		[seedHosts]
		Description:	Drops any HostTable data currently in the database and
						reseeds it from seed_data/hosts.json
		Input:			None
		Return:			None, reseeds HostTable
		------------------------------------------------------------------
	"""
	print("Seeding database's HostTable from \'%s\' in \'%s\' mode" %
		(hosts_json_path, mode))

	# Drop and recreate this table on option 'overwrite'
	if mode == 'overwrite':
		HostTable.__table__.drop(db.engine)
		db.metadata.create_all(db.engine, tables=[HostTable.__table__])

	# Populate database from json
	with open(hosts_json_path, mode='r') as hosts_json:
		hosts_content = json.loads(hosts_json.read())
		for entry in hosts_content["hosts"]:
			host_entry = HostTable(
				host_type=Host.to_enum(entry['host_type']),
				host_name=entry['host_name'],
				host_lang=Language.to_enum(entry['host_lang']),
				host_url=entry['host_url'],
				host_search_engine=entry['host_search_engine'])
			db.session.add(host_entry)
		db.session.commit()

def seedHonorifics(honorifics_json_path, mode='append'):
	"""-------------------------------------------------------------------
		Function:		[seedHonorifics]
		Description:	Drops any HonorificsTable data currently in the database
						and reseeds it from seed_data/honorifics.json
		Input:			None
		Return:			None, reseeds HostTable
		------------------------------------------------------------------
	"""
	print("Seeding database's HonorificsTable from \'%s\' in \'%s\' mode" %
		(honorifics_json_path, mode))

	# Drop and recreate this table on option 'overwrite'
	if mode == 'overwrite':
		HonorificsTable.__table__.drop(db.engine)
		db.metadata.create_all(db.engine, tables=[HonorificsTable.__table__])

	# Populate database from json
	with io.open(honorifics_json_path, mode='r', encoding='utf8') as honorifics_json:
		honorifics_content = json.loads(honorifics_json.read())
		for lang in Language:
			for entry in honorifics_content[Language.to_string(lang)]:
				honorific_entry = HonorificsTable(
					lang=lang,
					raw=entry["raw"],
					trans=entry["trans"],
					opt_standalone=entry["standalone"],
				)
				db.session.add(honorific_entry)
		db.session.commit()
